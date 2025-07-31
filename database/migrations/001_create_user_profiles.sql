-- Migration: 001_create_user_profiles.sql
-- Description: Creates user_profiles table with role enum for RBAC

-- Create role type enum
CREATE TYPE public.user_role AS ENUM ('admin', 'editor');

-- Create user_profiles table
CREATE TABLE public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    role user_role NOT NULL DEFAULT 'editor',
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add comment for documentation
COMMENT ON TABLE public.user_profiles IS 'Profile data for each user with role-based access control';

-- Create index for faster lookups
CREATE INDEX user_profiles_email_idx ON public.user_profiles (email);
CREATE INDEX user_profiles_role_idx ON public.user_profiles (role);

-- Set up RLS (Row Level Security)
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read all profiles
CREATE POLICY "Users can view all profiles" 
    ON public.user_profiles 
    FOR SELECT 
    USING (true);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile" 
    ON public.user_profiles 
    FOR UPDATE 
    USING (auth.uid() = id);

-- Policy: Only admins can create new profiles
CREATE POLICY "Only admins can create profiles" 
    ON public.user_profiles 
    FOR INSERT 
    WITH CHECK (
        auth.uid() IN (
            SELECT id FROM public.user_profiles WHERE role = 'admin'
        )
    );

-- Policy: Only admins can delete profiles
CREATE POLICY "Only admins can delete profiles" 
    ON public.user_profiles 
    FOR DELETE 
    USING (
        auth.uid() IN (
            SELECT id FROM public.user_profiles WHERE role = 'admin'
        )
    );

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update the updated_at column
CREATE TRIGGER update_user_profiles_updated_at
BEFORE UPDATE ON public.user_profiles
FOR EACH ROW
EXECUTE FUNCTION public.handle_updated_at();

-- Bootstrap first admin user (to be replaced with actual admin email)
-- This ensures there's at least one admin who can invite others
INSERT INTO public.user_profiles (id, email, full_name, role)
VALUES 
    ('00000000-0000-0000-0000-000000000000', 'admin@example.com', 'System Admin', 'admin')
ON CONFLICT (id) DO NOTHING;
