-- استشارة خبرات: schema + RLS
create extension if not exists pgcrypto;

create table if not exists public.consultation_requests (
  id uuid primary key default gen_random_uuid(),
  public_id text unique not null default ('KH-' || to_char(now(),'YYYY') || '-' || upper(substr(replace(gen_random_uuid()::text,'-',''),1,6))),
  full_name text not null,
  email text not null,
  phone text,
  country text,
  city text,
  role text,
  organization text,
  consultation_area text not null,
  challenge text not null check (char_length(challenge) between 10 and 800),
  tried text,
  desired_outcome text not null,
  current_stage text,
  reference_url text,
  urgency text,
  followup_interest text,
  scope_consent boolean not null default false,
  privacy_consent boolean not null default false,
  status text not null default 'new' check (status in ('new','reviewing','accepted','waitlist','declined','booked','completed')),
  score_relevance smallint check (score_relevance between 0 and 2),
  score_clarity smallint check (score_clarity between 0 and 2),
  score_30min_value smallint check (score_30min_value between 0 and 2),
  score_impact smallint check (score_impact between 0 and 2),
  score_readiness smallint check (score_readiness between 0 and 2),
  score smallint generated always as (
    coalesce(score_relevance,0)+coalesce(score_clarity,0)+coalesce(score_30min_value,0)+coalesce(score_impact,0)+coalesce(score_readiness,0)
  ) stored,
  reviewer_notes text,
  assigned_consultant text,
  booking_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.admin_users (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create or replace function public.set_updated_at() returns trigger language plpgsql as $$
begin new.updated_at=now(); return new; end; $$;

drop trigger if exists trg_consultation_updated_at on public.consultation_requests;
create trigger trg_consultation_updated_at
before update on public.consultation_requests
for each row execute function public.set_updated_at();

alter table public.consultation_requests enable row level security;
alter table public.admin_users enable row level security;

-- لا توجد سياسة INSERT عامة: استقبال الجمهور يتم حصراً عبر submit_consultation().
drop policy if exists "public can submit consultation" on public.consultation_requests;

drop policy if exists "admins can read consultation" on public.consultation_requests;
create policy "admins can read consultation"
on public.consultation_requests
for select to authenticated
using (exists(select 1 from public.admin_users a where a.user_id = auth.uid()));

drop policy if exists "admins can update consultation" on public.consultation_requests;
create policy "admins can update consultation"
on public.consultation_requests
for update to authenticated
using (exists(select 1 from public.admin_users a where a.user_id = auth.uid()))
with check (exists(select 1 from public.admin_users a where a.user_id = auth.uid()));

drop policy if exists "admins can see own admin row" on public.admin_users;
create policy "admins can see own admin row"
on public.admin_users
for select to authenticated
using (user_id = auth.uid());

create or replace function public.submit_consultation(payload jsonb)
returns text
language plpgsql
security definer
set search_path=public
as $$
declare
  rid text;
  v_name text := trim(coalesce(payload->>'full_name',''));
  v_email text := lower(trim(coalesce(payload->>'email','')));
  v_area text := trim(coalesce(payload->>'consultation_area',''));
  v_challenge text := trim(coalesce(payload->>'challenge',''));
  v_outcome text := trim(coalesce(payload->>'desired_outcome',''));
begin
  if coalesce((payload->>'scope_consent')::boolean,false) is not true
     or coalesce((payload->>'privacy_consent')::boolean,false) is not true then
    raise exception 'consent_required';
  end if;

  if char_length(v_name) < 2 or char_length(v_name) > 160 then raise exception 'invalid_name'; end if;
  if v_email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$' then raise exception 'invalid_email'; end if;
  if char_length(v_area) < 2 then raise exception 'invalid_area'; end if;
  if char_length(v_challenge) < 10 or char_length(v_challenge) > 800 then raise exception 'invalid_challenge'; end if;
  if char_length(v_outcome) < 5 or char_length(v_outcome) > 2000 then raise exception 'invalid_outcome'; end if;

  insert into public.consultation_requests(
    full_name,email,phone,country,city,role,organization,consultation_area,
    challenge,tried,desired_outcome,current_stage,reference_url,urgency,
    followup_interest,scope_consent,privacy_consent
  )
  values(
    v_name,v_email,nullif(trim(payload->>'phone'),''),
    nullif(trim(payload->>'country'),''),nullif(trim(payload->>'city'),''),
    nullif(trim(payload->>'role'),''),nullif(trim(payload->>'organization'),''),
    v_area,v_challenge,nullif(trim(payload->>'tried'),''),
    v_outcome,nullif(trim(payload->>'current_stage'),''),
    nullif(trim(payload->>'reference_url'),''),nullif(trim(payload->>'urgency'),''),
    nullif(trim(payload->>'followup_interest'),''),true,true
  )
  returning public_id into rid;

  return rid;
end $$;

revoke all on function public.submit_consultation(jsonb) from public;
grant execute on function public.submit_consultation(jsonb) to anon, authenticated;

-- بعد إنشاء مستخدم الإدارة من Supabase Auth نفّذ مرة واحدة:
-- insert into public.admin_users(user_id)
-- select id from auth.users where email='ADMIN_EMAIL_HERE';