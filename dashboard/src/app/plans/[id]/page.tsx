'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  FiArrowLeft, 
  FiEdit, 
  FiTrash2, 
  FiPlus, 
  FiFileText, 
  FiAlertCircle, 
  FiRefreshCw,
  FiGlobe,
  FiUsers,
  FiMessageSquare,
  FiTarget,
  FiCheck,
  FiClock,
  FiImage
} from 'react-icons/fi';
import supabase from '@/lib/supabase';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

// Define types
type StrategicPlan = {
  id: string;
  domain: string;
  audience: string;
  tone: string;
  niche: string;
  goal: string;
  wordpress_site_id: string;
  created_at: string;
  updated_at: string | null;
};

type WordPressSite = {
  id: string;
  domain: string;
  url: string;
  username: string;
  app_password: string;
  created_at: string;
  updated_at: string | null;
};

type ContentPiece = {
  id: string;
  title: string;
  slug: string;
  status: string;
  draft_text: string | null;
  featured_image_id: string | null;
  wordpress_post_id: number | null;
  wordpress_post_url: string | null;
  strategic_plan_id: string;
  created_at: string;
  updated_at: string | null;
  published_at: string | null;
};

export default function StrategicPlanDetail({ params }: { params: { id: string } }) {
  const router = useRouter();
  const planId = params.id;
  
  // State
  const [plan, setPlan] = useState<StrategicPlan | null>(null);
  const [wordpressSite, setWordpressSite] = useState<WordPressSite | null>(null);
  const [contentPieces, setContentPieces] = useState<ContentPiece[]>([]);
  const [loading, setLoading] = useState(true);
  const [contentLoading, setContentLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const itemsPerPage = 10;
  
  // Fetch strategic plan data
  useEffect(() => {
    async function fetchPlanData() {
      try {
        setLoading(true);
        
        // Fetch strategic plan
        const { data: planData, error: planError } = await supabase
          .from('strategic_plans')
          .select('*')
          .eq('id', planId)
          .single();
        
        if (planError) throw new Error(planError.message);
        if (!planData) throw new Error('Strategic plan not found');
        
        setPlan(planData);
        
        // Fetch associated WordPress site
        if (planData.wordpress_site_id) {
          const { data: siteData, error: siteError } = await supabase
            .from('wordpress_sites')
            .select('*')
            .eq('id', planData.wordpress_site_id)
            .single();
          
          if (!siteError && siteData) {
            setWordpressSite(siteData);
          }
        }
        
      } catch (err) {
        console.error('Error fetching strategic plan data:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    }
    
    fetchPlanData();
  }, [planId]);
  
  // Fetch content pieces associated with this plan
  useEffect(() => {
    async function fetchContentPieces() {
      try {
        setContentLoading(true);
        
        // Calculate pagination
        const from = (currentPage - 1) * itemsPerPage;
        const to = from + itemsPerPage - 1;
        
        // Fetch content pieces with pagination
        const { data, count, error } = await supabase
          .from('content_pieces')
          .select('*', { count: 'exact' })
          .eq('strategic_plan_id', planId)
          .order('created_at', { ascending: false })
          .range(from, to);
        
        if (error) throw new Error(error.message);
        
        setContentPieces(data || []);
        if (count !== null) setTotalCount(count);
        
      } catch (err) {
        console.error('Error fetching content pieces:', err);
        toast.error('Failed to load content pieces');
      } finally {
        setContentLoading(false);
      }
    }
    
    if (planId) {
      fetchContentPieces();
    }
  }, [planId, currentPage]);
  
  // Handle delete plan
  const handleDeletePlan = async () => {
    if (!confirm('Are you sure you want to delete this strategic plan? This will also delete all associated content pieces.')) {
      return;
    }
    
    try {
      setDeleteLoading(true);
      
      // First, check if there are any content pieces using this plan
      const { count, error: countError } = await supabase
        .from('content_pieces')
        .select('*', { count: 'exact', head: true })
        .eq('strategic_plan_id', planId);
      
      if (countError) throw new Error(countError.message);
      
      if (count && count > 0) {
        // Ask for additional confirmation if content pieces exist
        if (!confirm(`This plan has ${count} content pieces associated with it. Deleting will remove all of them. Continue?`)) {
          setDeleteLoading(false);
          return;
        }
        
        // Delete associated content pieces first
        const { error: deleteContentError } = await supabase
          .from('content_pieces')
          .delete()
          .eq('strategic_plan_id', planId);
        
        if (deleteContentError) throw new Error(deleteContentError.message);
      }
      
      // Now delete the plan
      const { error: deletePlanError } = await supabase
        .from('strategic_plans')
        .delete()
        .eq('id', planId);
      
      if (deletePlanError) throw new Error(deletePlanError.message);
      
      toast.success('Strategic plan deleted successfully');
      
      // Redirect to plans list
      router.push('/plans');
      
    } catch (err) {
      console.error('Error deleting strategic plan:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      toast.error('Failed to delete strategic plan');
    } finally {
      setDeleteLoading(false);
    }
  };
  
  // Helper function to get status badge color
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'researched': return 'bg-blue-100 text-blue-800';
      case 'written': return 'bg-purple-100 text-purple-800';
      case 'flow_edited': return 'bg-indigo-100 text-indigo-800';
      case 'line_edited': return 'bg-cyan-100 text-cyan-800';
      case 'image_generated': return 'bg-teal-100 text-teal-800';
      case 'published': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Helper function to get status icon
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'draft': return <FiFileText className="text-gray-500" />;
      case 'researched': return <FiClock className="text-blue-500" />;
      case 'written': return <FiEdit className="text-purple-500" />;
      case 'flow_edited': return <FiEdit className="text-indigo-500" />;
      case 'line_edited': return <FiEdit className="text-cyan-500" />;
      case 'image_generated': return <FiImage className="text-green-500" />;
      case 'published': return <FiCheck className="text-green-600" />;
      default: return <FiFileText className="text-gray-500" />;
    }
  };
  
  // Format status for display
  const formatStatus = (status: string) => {
    return status
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };
  
  // Calculate total pages for pagination
  const totalPages = Math.ceil(totalCount / itemsPerPage);

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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Strategic Plan Details</h1>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-300 rounded-md text-red-800 flex items-center">
          <FiAlertCircle className="mr-2 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}
      
      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}
      
      {/* Strategic plan details */}
      {!loading && !error && plan && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main content area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Plan header */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  {plan.domain} - {plan.niche}
                </h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-300">
                <div>
                  <p><span className="font-medium">Created:</span> {format(new Date(plan.created_at), 'MMM d, yyyy')}</p>
                  {plan.updated_at && (
                    <p><span className="font-medium">Last Updated:</span> {format(new Date(plan.updated_at), 'MMM d, yyyy')}</p>
                  )}
                </div>
              </div>
              
              {/* WordPress site info */}
              {wordpressSite && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center">
                    <FiGlobe className="mr-2 text-gray-500 dark:text-gray-400" />
                    <span className="font-medium text-gray-700 dark:text-gray-300">WordPress Site:</span>
                    <a 
                      href={wordpressSite.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="ml-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                    >
                      {wordpressSite.domain}
                    </a>
                  </div>
                </div>
              )}
            </div>
            
            {/* Plan details */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
              <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Plan Details</h3>
              
              <div className="space-y-4">
                {/* Audience */}
                <div>
                  <div className="flex items-center">
                    <FiUsers className="mr-2 text-gray-500 dark:text-gray-400" />
                    <h4 className="text-md font-medium text-gray-900 dark:text-white">Target Audience</h4>
                  </div>
                  <p className="mt-1 text-gray-600 dark:text-gray-300 pl-6">{plan.audience}</p>
                </div>
                
                {/* Tone */}
                <div>
                  <div className="flex items-center">
                    <FiMessageSquare className="mr-2 text-gray-500 dark:text-gray-400" />
                    <h4 className="text-md font-medium text-gray-900 dark:text-white">Content Tone</h4>
                  </div>
                  <p className="mt-1 text-gray-600 dark:text-gray-300 pl-6">{plan.tone}</p>
                </div>
                
                {/* Niche */}
                <div>
                  <div className="flex items-center">
                    <FiTarget className="mr-2 text-gray-500 dark:text-gray-400" />
                    <h4 className="text-md font-medium text-gray-900 dark:text-white">Content Niche</h4>
                  </div>
                  <p className="mt-1 text-gray-600 dark:text-gray-300 pl-6">{plan.niche}</p>
                </div>
                
                {/* Goal */}
                <div>
                  <div className="flex items-start">
                    <FiTarget className="mr-2 mt-1 text-gray-500 dark:text-gray-400" />
                    <div>
                      <h4 className="text-md font-medium text-gray-900 dark:text-white">Content Goals</h4>
                      <p className="mt-1 text-gray-600 dark:text-gray-300 whitespace-pre-line">{plan.goal}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Content pieces */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Content Pieces</h3>
                <Link
                  href={`/content/new?plan=${plan.id}`}
                  className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                >
                  <FiPlus className="mr-1.5" />
                  Create Content
                </Link>
              </div>
              
              {contentLoading ? (
                <div className="flex justify-center items-center py-12">
                  <FiRefreshCw className="animate-spin text-blue-600 mr-2" />
                  <span className="text-gray-600 dark:text-gray-300">Loading content pieces...</span>
                </div>
              ) : contentPieces.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                          Title
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                          Status
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                          Created
                        </th>
                        <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                      {contentPieces.map((content) => (
                        <tr key={content.id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">{content.title}</div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">{content.slug}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(content.status)}`}>
                              <span className="mr-1">{getStatusIcon(content.status)}</span>
                              {formatStatus(content.status)}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {format(new Date(content.created_at), 'MMM d, yyyy')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex justify-end space-x-2">
                              <Link
                                href={`/content/${content.id}`}
                                className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                              >
                                <span className="sr-only">View</span>
                                <FiFileText size={18} />
                              </Link>
                              {content.wordpress_post_url && (
                                <a
                                  href={content.wordpress_post_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                                >
                                  <span className="sr-only">View on WordPress</span>
                                  <FiGlobe size={18} />
                                </a>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-8 text-center text-gray-500 dark:text-gray-400">
                  <p>No content pieces found for this strategic plan.</p>
                  <p className="text-sm mt-2">
                    Click the "Create Content" button to add your first piece.
                  </p>
                </div>
              )}
              
              {/* Pagination */}
              {totalPages > 1 && (
                <div className="px-6 py-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700">
                  <div className="flex-1 flex justify-between sm:hidden">
                    <button
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                      className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                        currentPage === 1
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500 dark:border-gray-600'
                          : 'bg-white text-gray-700 hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700 dark:border-gray-600'
                      }`}
                    >
                      Previous
                    </button>
                    <button
                      onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                      disabled={currentPage === totalPages}
                      className={`ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                        currentPage === totalPages
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500 dark:border-gray-600'
                          : 'bg-white text-gray-700 hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700 dark:border-gray-600'
                      }`}
                    >
                      Next
                    </button>
                  </div>
                  <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        Showing <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> to{' '}
                        <span className="font-medium">
                          {Math.min(currentPage * itemsPerPage, totalCount)}
                        </span>{' '}
                        of <span className="font-medium">{totalCount}</span> results
                      </p>
                    </div>
                    <div>
                      <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                        <button
                          onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                          disabled={currentPage === 1}
                          className={`relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 text-sm font-medium ${
                            currentPage === 1
                              ? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500 dark:border-gray-600'
                              : 'bg-white text-gray-500 hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:border-gray-600'
                          }`}
                        >
                          <span className="sr-only">Previous</span>
                          <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </button>
                        
                        {/* Page numbers */}
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          let pageNum;
                          if (totalPages <= 5) {
                            // Show all pages if 5 or fewer
                            pageNum = i + 1;
                          } else if (currentPage <= 3) {
                            // Near the start
                            pageNum = i + 1;
                          } else if (currentPage >= totalPages - 2) {
                            // Near the end
                            pageNum = totalPages - 4 + i;
                          } else {
                            // In the middle
                            pageNum = currentPage - 2 + i;
                          }
                          
                          return (
                            <button
                              key={pageNum}
                              onClick={() => setCurrentPage(pageNum)}
                              className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                                currentPage === pageNum
                                  ? 'z-10 bg-blue-50 border-blue-500 text-blue-600 dark:bg-blue-900 dark:border-blue-500 dark:text-blue-200'
                                  : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700'
                              }`}
                            >
                              {pageNum}
                            </button>
                          );
                        })}
                        
                        <button
                          onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                          disabled={currentPage === totalPages}
                          className={`relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 text-sm font-medium ${
                            currentPage === totalPages
                              ? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500 dark:border-gray-600'
                              : 'bg-white text-gray-500 hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:border-gray-600'
                          }`}
                        >
                          <span className="sr-only">Next</span>
                          <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                          </svg>
                        </button>
                      </nav>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Actions card */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
              <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Actions</h3>
              
              <div className="space-y-3">
                {/* Create content button */}
                <Link
                  href={`/content/new?plan=${plan.id}`}
                  className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  <FiPlus className="mr-2" />
                  Create Content
                </Link>
                
                {/* Edit button */}
                <Link
                  href={`/plans/${plan.id}/edit`}
                  className="w-full flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
                >
                  <FiEdit className="mr-2" />
                  Edit Plan
                </Link>
                
                {/* Delete button */}
                <button
                  onClick={handleDeletePlan}
                  disabled={deleteLoading}
                  className="w-full flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:bg-red-400 disabled:cursor-not-allowed"
                >
                  {deleteLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Deleting...
                    </>
                  ) : (
                    <>
                      <FiTrash2 className="mr-2" />
                      Delete Plan
                    </>
                  )}
                </button>
              </div>
            </div>
            
            {/* Stats card */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
              <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Content Stats</h3>
              
              {!contentLoading ? (
                <div className="space-y-3">
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    <span className="font-medium">Total Content Pieces:</span> {totalCount}
                  </p>
                  
                  {/* We could add more stats here like: */}
                  {/* <p className="text-sm text-gray-600 dark:text-gray-300">
                    <span className="font-medium">Published:</span> {publishedCount}
                  </p> */}
                </div>
              ) : (
                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <FiRefreshCw className="animate-spin mr-2" />
                  Loading stats...
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
