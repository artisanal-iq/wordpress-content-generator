'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { FiPlusCircle, FiFileText, FiCheck, FiAlertCircle, FiClock, FiEdit, FiImage, FiUpload } from 'react-icons/fi';
import supabase from '@/lib/supabase';
import { format } from 'date-fns';

// Define types for our content data
type ContentPiece = {
  id: string;
  title: string;
  status: string;
  created_at: string;
  updated_at: string | null;
};

type StatusCount = {
  [key: string]: number;
};

export default function Home() {
  // Canonical order of pipeline statuses
  const allStatuses = [
    'draft',
    'researched',
    'written',
    'flow_edited',
    'line_edited',
    'image_generated',
    'published'
  ];

  // State for dashboard data
  const [contentStats, setContentStats] = useState<StatusCount>({});
  const [recentContent, setRecentContent] = useState<ContentPiece[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch dashboard data
  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setLoading(true);
        
        // Fetch content statistics
        const { data: statusData, error: statusError } = await supabase
          .from('content_pieces')
          .select('status');
        
        if (statusError) throw new Error(statusError.message);
        
        // Calculate counts by status
        // Start every status at 0 so we always have a KPI card
        const counts: StatusCount = {};
        allStatuses.forEach(s => (counts[s] = 0));
        statusData?.forEach(item => {
          counts[item.status] = (counts[item.status] || 0) + 1;
        });
        setContentStats(counts);
        
        // Fetch recent content
        const { data: recentData, error: recentError } = await supabase
          .from('content_pieces')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(5);
        
        if (recentError) throw new Error(recentError.message);
        setRecentContent(recentData || []);
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    }
    
    fetchDashboardData();
  }, []);

  // Helper function to get appropriate icon for content status
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
  
  // Helper function to get color for status cards
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'draft': return 'bg-gray-100 border-gray-300 text-gray-800';
      case 'researched': return 'bg-blue-50 border-blue-300 text-blue-800';
      case 'written': return 'bg-purple-50 border-purple-300 text-purple-800';
      case 'flow_edited': return 'bg-indigo-50 border-indigo-300 text-indigo-800';
      case 'line_edited': return 'bg-cyan-50 border-cyan-300 text-cyan-800';
      case 'image_generated': return 'bg-teal-50 border-teal-300 text-teal-800';
      case 'published': return 'bg-green-50 border-green-300 text-green-800';
      default: return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };
  
  // Helper function to get human-readable status
  const formatStatus = (status: string) => {
    return status
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <Link 
          href="/content/new" 
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <FiPlusCircle className="mr-2" />
          Create Content
        </Link>
        <Link 
          href="/plans/new" 
          className="ml-2 inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          <FiPlusCircle className="mr-2" />
          Create Plan
        </Link>
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
      
      {!loading && !error && (
        <>
          {/* Stats cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {allStatuses.map(status => (
              <div 
                key={status}
                className={`p-4 rounded-lg border ${getStatusColor(status)} flex items-center justify-between`}
              >
                <div>
                  <p className="text-sm font-medium">{formatStatus(status)}</p>
                  <p className="text-2xl font-bold">{contentStats[status] ?? 0}</p>
                </div>
                <div className="text-2xl">
                  {getStatusIcon(status)}
                </div>
              </div>
            ))}
          </div>
          
          {/* Pipeline visualization */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
            <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Content Pipeline</h2>
            <div className="flex flex-wrap items-center gap-2">
              {['draft', 'researched', 'written', 'flow_edited', 'line_edited', 'image_generated', 'published'].map((status, index, array) => (
                <div key={status} className="flex items-center">
                  <div className={`
                    flex items-center justify-center w-10 h-10 rounded-full 
                    ${contentStats[status] ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500 dark:bg-gray-700'}
                  `}>
                    {contentStats[status] || 0}
                  </div>
                  <div className="mx-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                    {formatStatus(status)}
                  </div>
                  {index < array.length - 1 && (
                    <div className="w-4 h-0.5 bg-gray-300 dark:bg-gray-600 mx-1"></div>
                  )}
                </div>
              ))}
            </div>
          </div>
          
          {/* Recent content */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
            <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Recent Content</h2>
            {recentContent.length > 0 ? (
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {recentContent.map(content => (
                  <Link 
                    key={content.id} 
                    href={`/content/${content.id}`}
                    className="flex items-center justify-between py-3 hover:bg-gray-50 dark:hover:bg-gray-750 px-2 rounded-md transition-colors"
                  >
                    <div className="flex items-center">
                      <div className="mr-3">
                        {getStatusIcon(content.status)}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{content.title}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {formatStatus(content.status)} • Created {format(new Date(content.created_at), 'MMM d, yyyy')}
                        </p>
                      </div>
                    </div>
                    <div className="text-gray-400">
                      <FiFileText />
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 dark:text-gray-400 py-4 text-center">No content pieces found</p>
            )}
            
            <div className="mt-4 text-center">
              <Link 
                href="/content" 
                className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
              >
                View all content →
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
