'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { FiArrowLeft, FiAlertCircle, FiSave, FiLoader } from 'react-icons/fi';
import supabase from '@/lib/supabase';
import toast from 'react-hot-toast';

// Define types
type StrategicPlan = {
  id: string;
  domain: string;
  niche: string;
  audience: string;
};

export default function CreateContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedPlanId = searchParams.get('plan') ?? '';
  
  // Form state
  const [title, setTitle] = useState('');
  const [strategicPlanId, setStrategicPlanId] = useState('');
  const [plans, setPlans] = useState<StrategicPlan[]>([]);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [plansLoading, setPlansLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch strategic plans for dropdown
  useEffect(() => {
    async function fetchStrategicPlans() {
      try {
        setPlansLoading(true);
        
        const { data, error } = await supabase
          .from('strategic_plans')
          .select('id, domain, niche, audience')
          .order('created_at', { ascending: false });
        
        if (error) throw new Error(error.message);
        
        const fetchedPlans = data || [];
        setPlans(fetchedPlans);

        // If a plan id is provided in the URL and not yet selected, pre-select it
        if (preselectedPlanId && !strategicPlanId) {
          const match = fetchedPlans.find(p => p.id === preselectedPlanId);
          if (match) {
            setStrategicPlanId(preselectedPlanId);
          }
        }
      } catch (err) {
        console.error('Error fetching strategic plans:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setPlansLoading(false);
      }
    }
    
    fetchStrategicPlans();
  }, []);
  
  // Generate slug from title
  const generateSlug = (text: string) => {
    return text
      .toLowerCase()
      .replace(/[^\w\s-]/g, '') // Remove special characters
      .replace(/\s+/g, '-')     // Replace spaces with hyphens
      .replace(/-+/g, '-')      // Remove consecutive hyphens
      .trim();
  };
  
  // Form submission handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    
    if (!strategicPlanId) {
      setError('Strategic plan is required');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Generate slug from title
      const slug = generateSlug(title);
      
      // Create content piece
      const { data, error } = await supabase
        .from('content_pieces')
        .insert({
          title,
          slug,
          strategic_plan_id: strategicPlanId,
          status: 'draft',
          created_at: new Date().toISOString()
        })
        .select()
        .single();
      
      if (error) throw new Error(error.message);
      
      if (!data) throw new Error('Failed to create content piece');
      
      // Show success message
      toast.success('Content piece created successfully!');
      
      // Redirect to content detail page
      router.push(`/content/${data.id}`);
      
    } catch (err) {
      console.error('Error creating content piece:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      toast.error('Failed to create content piece');
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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create New Content</h1>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-300 rounded-md text-red-800 flex items-center">
          <FiAlertCircle className="mr-2 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}
      
      {/* Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title input */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Title *
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter content title"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              required
            />
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              The title of your content piece. This will be used to generate a URL slug.
            </p>
          </div>
          
          {/* Strategic plan dropdown */}
          <div>
            <label htmlFor="strategicPlan" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Strategic Plan *
            </label>
            {plansLoading ? (
              <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
                <FiLoader className="animate-spin" />
                <span>Loading strategic plans...</span>
              </div>
            ) : (
              <>
                <select
                  id="strategicPlan"
                  value={strategicPlanId}
                  onChange={(e) => setStrategicPlanId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  required
                >
                  <option value="">Select a strategic plan</option>
                  {plans.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.domain} - {plan.niche} ({plan.audience})
                    </option>
                  ))}
                </select>
                {plans.length === 0 && (
                  <p className="mt-1 text-sm text-yellow-600 dark:text-yellow-400">
                    No strategic plans found. <Link href="/plans/new" className="underline">Create one first</Link>.
                  </p>
                )}
              </>
            )}
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              The strategic plan this content belongs to. This determines the target audience and goals.
            </p>
          </div>
          
          {/* Submit button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading || plansLoading || plans.length === 0}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <FiLoader className="animate-spin mr-2" />
                  Creating...
                </>
              ) : (
                <>
                  <FiSave className="mr-2" />
                  Create Content
                </>
              )}
            </button>
          </div>
        </form>
      </div>
      
      {/* Help box */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">What happens next?</h3>
        <p className="text-sm text-blue-700 dark:text-blue-400">
          After creating a content piece, it will be in <strong>Draft</strong> status. You can then run the Research Agent 
          to gather information, followed by the Draft Writer Agent to create the initial content.
        </p>
      </div>
    </div>
  );
}
