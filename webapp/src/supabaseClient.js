import { createClient } from '@supabase/supabase-js';

// We will use standard environment variables or hardcode for now for simplicity
const supabaseUrl = 'https://gjdjqnffelyxsgzzgpmn.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdqZGpxbmZmZWx5eHNnenpncG1uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODEzODY5NzAsImV4cCI6MjA5Njk2Mjk3MH0.ox1BitnRY0KGuWz40TnwCrqd_zr2iJ_f0LkHEG77Hi4';

export const supabase = createClient(supabaseUrl, supabaseKey);
