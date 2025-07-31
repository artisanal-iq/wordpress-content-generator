-- Migration: 002_update_wordpress_sites.sql
-- Description: Add scaffold tracking columns to wordpress_sites table

-- Create scaffold status enum type
CREATE TYPE public.scaffold_status AS ENUM (
    'not_started',
    'in_progress',
    'done',
    'failed'
);

-- Add scaffold tracking columns to wordpress_sites table
ALTER TABLE public.wordpress_sites 
    ADD COLUMN scaffold_status scaffold_status NOT NULL DEFAULT 'not_started',
    ADD COLUMN scaffolded_at TIMESTAMPTZ;

-- Add comment for documentation
COMMENT ON COLUMN public.wordpress_sites.scaffold_status IS 'Status of the WordPress site scaffolding process';
COMMENT ON COLUMN public.wordpress_sites.scaffolded_at IS 'Timestamp when site scaffolding was completed';

-- Create index for efficient filtering by scaffold status
CREATE INDEX wordpress_sites_scaffold_status_idx ON public.wordpress_sites (scaffold_status);
