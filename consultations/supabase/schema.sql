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
  challenge text not null check (char_length(challenge) <= 800),
  tried text,
  desired_outcome text not null,
  current_stage text,
  reference_url text,
  urgency text,
  followup_interest text,
  scope_consent boolean not null default false,
  privacy_consent boolean not null default false,
  status text not null default 'new' check (status in ('new','reviewing','accepted','waitlist','declined','booked','completed')),
  score integer check (score between 0 and 10),
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

drop policy if exists "public can submit consultation" on public.consultation_requests;
create policy "public can submit consultation"
on public.consultation_requests
for insert to anon
with check (scope_consent = true and privacy_consent = true);

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
declare rid text;
begin
  if coalesce((payload->>'scope_consent')::boolean,false) is not true
     or coalesce((payload->>'privacy_consent')::boolean,false) is not true then
    raise exception 'consent_required';
  end if;

  insert into public.consultation_requests(
    full_name,email,phone,country,city,role,organization,consultation_area,
    challenge,tried,desired_outcome,current_stage,reference_url,urgency,
    followup_interest,scope_consent,privacy_consent
  )
  values(
    payload->>'full_name',payload->>'email',payload->>'phone',payload->>'country',
    payload->>'city',payload->>'role',payload->>'organization',payload->>'consultation_area',
    payload->>'challenge',payload->>'tried',payload->>'desired_outcome',
    payload->>'current_stage',payload->>'reference_url',payload->>'urgency',
    payload->>'followup_interest',true,true
  )
  returning public_id into rid;

  return rid;
end $$;

revoke all on function public.submit_consultation(jsonb) from public;
grant execute on function public.submit_consultation(jsonb) to anon, authenticated;

-- بعد إنشاء مستخدم الإدارة من Supabase Auth نفّذ مرة واحدة:
-- insert into public.admin_users(user_id)
-- select id from auth.users where email='ADMIN_EMAIL_HERE';