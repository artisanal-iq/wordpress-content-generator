'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FiArrowLeft, FiAlertCircle, FiSave, FiLoader } from 'react-icons/fi';
import supabase from '@/lib/supabase';
import toast from 'react-hot-toast';

export default function EditStrategicPlan({ params }: { params: { id: string } }) {
  const router = useRouter();
  const planId = params.id;
  
  // Form state
  const [formData, setFormData] = useState({
    domain: '',
    audience: '',
    tone: '',
    niche: '',
    goal: '',
    wordpressSiteId: ''
  });

  // WordPress sites for dropdown
  const [sites, setSites] = useState<{ id: string; domain: string }[]>([]);
  const [sitesLoading, setSitesLoading] = useState(true);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch plan data and WordPress sites on mount
  useEffect(() => {
    async function fetchData() {
      try {
        setInitialLoading(true);
        
        // Fetch the strategic plan
        const { data: planData, error: planError } = await supabase
          .from('strategic_plans')
          .select('*')
          .eq('id', planId)
          .single();
        
        if (planError) throw new Error(planError.message);
        if (!planData) throw new Error('Strategic plan not found');
        
        // Set form data from plan
        setFormData({
          domain: planData.domain,
          audience: planData.audience,
          tone: planData.tone,
          niche: planData.niche,
          goal: planData.goal,
          wordpressSiteId: planData.wordpress_site_id
        });
        
        // Fetch WordPress sites
        const { data: sitesData, error: sitesError } = await supabase
          .from('wordpress_sites')
          .select('id, domain')
          .order('domain');
        
        if (sitesError) throw new Error(sitesError.message);
        setSites(sitesData || []);
        
      } catch (err) {
        console.error('Error loading data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load plan data');
        toast.error('Failed to load plan data');
      } finally {
        setInitialLoading(false);
        setSitesLoading(false);
      }
    }
    
    fetchData();
  }, [planId]);

  // Handle form input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Form submission handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const { domain, audience, tone, niche, goal, wordpressSiteId } = formData;
    
    if (!domain.trim()) {
      setError('Domain is required');
      return;
    }
    
    if (!audience.trim()) {
      setError('Target audience is required');
      return;
    }
    
    if (!tone.trim()) {
      setError('Content tone is required');
      return;
    }
    
    if (!niche.trim()) {
      setError('Content niche is required');
      return;
    }
    
    if (!goal.trim()) {
      setError('Content goal is required');
      return;
    }

    if (!wordpressSiteId) {
      setError('Please choose a WordPress site');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Update strategic plan
      const { error } = await supabase
        .from('strategic_plans')
        .update({
          domain,
          audience,
          tone,
          niche,
          goal,
          wordpress_site_id: wordpressSiteId,
          updated_at: new Date().toISOString()
        })
        .eq('id', planId);
      
      if (error) throw new Error(error.message);
      
      // Show success message
      toast.success('Strategic plan updated successfully!');
      
      // Redirect to plan detail page
      router.push(`/plans/${planId}`);
      
    } catch (err) {
      console.error('Error updating strategic plan:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      toast.error('Failed to update strategic plan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page header with back button */}
      <div className="flex items-center gap-4">
        <button 
          onClick={() => router.back()}
          className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700"
        >
          <FiArrowLeft className="text-gray-600 dark:text-gray-300" />
        </button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Edit Strategic Plan</h1>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-300 rounded-md text-red-800 flex items-center">
          <FiAlertCircle className="mr-2 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}
      
      {/* Loading state */}
      {initialLoading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        /* Form */
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Domain input */}
            <div>
              <label htmlFor="domain" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Domain *
              </label>
              <input
                type="text"
                id="domain"
                name="domain"
                value={formData.domain}
                onChange={handleChange}
                placeholder="example.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                The website domain where content will be published.
              </p>
            </div>
            
            {/* Audience input */}
            <div>
              <label htmlFor="audience" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Target Audience *
              </label>
              <input
                type="text"
                id="audience"
                name="audience"
                value={formData.audience}
                onChange={handleChange}
                placeholder="e.g., Tech professionals, Parents, Fitness enthusiasts"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Who is the primary audience for your content?
              </p>
            </div>
            
            {/* Tone select */}
            <div>
              <label htmlFor="tone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Content Tone *
              </label>
              <select
                id="tone"
                name="tone"
                value={formData.tone}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              >
                <option value="">Select a tone</option>
                <option value="informative">Informative</option>
                <option value="conversational">Conversational</option>
                <option value="professional">Professional</option>
                <option value="authoritative">Authoritative</option>
                <option value="friendly">Friendly</option>
                <option value="humorous">Humorous</option>
                <option value="formal">Formal</option>
                <option value="casual">Casual</option>
              </select>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                The overall tone and voice for your content.
              </p>
            </div>
            
            {/* Niche input */}
            <div>
              <label htmlFor="niche" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Content Niche *
              </label>
              <input
                type="text"
                id="niche"
                name="niche"
                value={formData.niche}
                onChange={handleChange}
                placeholder="e.g., Technology, Health, Finance"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                The main topic area or industry for your content.
              </p>
            </div>
            
            {/* Goal textarea */}
            <div>
              <label htmlFor="goal" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Content Goals *
              </label>
              <textarea
                id="goal"
                name="goal"
                value={formData.goal}
                onChange={handleChange}
                placeholder="e.g., Educate readers, Generate leads, Build brand awareness"
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                What are the primary goals for your content strategy?
              </p>
            </div>

            {/* WordPress site selector */}
            <div>
              <label htmlFor="wordpressSiteId" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                WordPress Site *
              </label>
              {sitesLoading ? (
                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <FiLoader className="animate-spin mr-2" />
                  Loading WordPress sites...
                </div>
              ) : (
                <select
                  id="wordpressSiteId"
                  name="wordpressSiteId"
                  value={formData.wordpressSiteId}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  required
                >
                  <option value="">Select a WordPress site</option>
                  {sites.map(site => (
                    <option key={site.id} value={site.id}>
                      {site.domain}
                    </option>
                  ))}
                </select>
              )}
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Choose which connected WordPress site this plan will publish to.
              </p>
            </div>
            
            {/* Submit button */}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <FiLoader className="animate-spin mr-2" />
                    Saving...
                  </>
                ) : (
                  <>
                    <FiSave className="mr-2" />
                    Update Plan
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
