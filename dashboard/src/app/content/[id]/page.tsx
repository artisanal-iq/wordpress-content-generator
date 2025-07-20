'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { 
  FiArrowLeft, 
  FiFileText, 
  FiCheck, 
  FiAlertCircle, 
  FiClock, 
  FiEdit, 
  FiImage, 
  FiUpload,
  FiPlay,
  FiTag,
  FiList,
  FiActivity,
  FiExternalLink,
  FiRefreshCw,
  FiGlobe
} from 'react-icons/fi';
import supabase from '@/lib/supabase';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

// Define types
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

type Keywords = {
  id: string;
  content_id: string;
  focus_keyword: string;
  supporting_keywords: string[];
  created_at: string;
};

type Image = {
  id: string;
  content_id: string;
  file_path: string;
  metadata: Record<string, any>;
  created_at: string;
};

type AgentStatus = {
  id: string;
  content_id: string;
  agent: string;
  status: string;
  input: Record<string, any> | null;
  output: Record<string, any> | null;
  error: Record<string, any> | null;
  created_at: string;
};

type Tab = 'content' | 'keywords' | 'images' | 'pipeline';

export default function ContentDetail({ params }: { params: { id: string } }) {
  const router = useRouter();
  const contentId = params.id;
  
  // State
  const [content, setContent] = useState<ContentPiece | null>(null);
  const [strategicPlan, setStrategicPlan] = useState<StrategicPlan | null>(null);
  const [wordpressSite, setWordpressSite] = useState<WordPressSite | null>(null);
  const [keywords, setKeywords] = useState<Keywords | null>(null);
  const [image, setImage] = useState<Image | null>(null);
  const [agentLogs, setAgentLogs] = useState<AgentStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('content');
  
  // Fetch content data
  useEffect(() => {
    async function fetchContentData() {
      try {
        setLoading(true);
        
        // Fetch content piece
        const { data: contentData, error: contentError } = await supabase
          .from('content_pieces')
          .select('*')
          .eq('id', contentId)
          .single();
        
        if (contentError) throw new Error(contentError.message);
        if (!contentData) throw new Error('Content piece not found');
        
        setContent(contentData);
        
        // Fetch strategic plan
        const { data: planData, error: planError } = await supabase
          .from('strategic_plans')
          .select('*')
          .eq('id', contentData.strategic_plan_id)
          .single();
        
        if (planError) throw new Error(planError.message);
        if (planData) {
          setStrategicPlan(planData);
          
          // Fetch WordPress site
          const { data: siteData, error: siteError } = await supabase
            .from('wordpress_sites')
            .select('*')
            .eq('id', planData.wordpress_site_id)
            .single();
          
          if (!siteError && siteData) {
            setWordpressSite(siteData);
          }
        }
        
        // Fetch keywords
        const { data: keywordsData } = await supabase
          .from('keywords')
          .select('*')
          .eq('content_id', contentId)
          .single();
        
        setKeywords(keywordsData || null);
        
        // Fetch image if exists
        if (contentData.featured_image_id) {
          const { data: imageData } = await supabase
            .from('images')
            .select('*')
            .eq('id', contentData.featured_image_id)
            .single();
          
          setImage(imageData || null);
        }
        
        // Fetch agent logs
        const { data: logsData } = await supabase
          .from('agent_status')
          .select('*')
          .eq('content_id', contentId)
          .order('created_at', { ascending: false });
        
        setAgentLogs(logsData || []);
        
      } catch (err) {
        console.error('Error fetching content data:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    }
    
    fetchContentData();
  }, [contentId]);

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
  
  // Helper function to get color for status badges
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
  
  // Helper function to get human-readable status
  const formatStatus = (status: string) => {
    return status
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };
  
  // Helper function to get agent name from agent string
  const getAgentName = (agent: string) => {
    return agent
      .replace(/-agent$/, '')
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };
  
  // Function to determine the next agent based on current status
  const getNextAgent = (status: string) => {
    switch (status.toLowerCase()) {
      case 'draft': return { name: 'Research Agent', agent: 'research-agent' };
      case 'researched': return { name: 'Draft Writer Agent', agent: 'draft-writer-agent' };
      case 'written': return { name: 'Flow Editor Agent', agent: 'flow-editor-agent' };
      case 'flow_edited': return { name: 'Line Editor Agent', agent: 'line-editor-agent' };
      case 'line_edited': return { name: 'Image Generator Agent', agent: 'image-generator-agent' };
      case 'image_generated': return { name: 'WordPress Publisher Agent', agent: 'wordpress-publisher-agent' };
      default: return null;
    }
  };
  
  // Function to run the next agent
  const runNextAgent = async () => {
    if (!content) return;
    
    const nextAgent = getNextAgent(content.status);
    if (!nextAgent) {
      toast.error('No next agent available for this content status');
      return;
    }
    
    try {
      setActionLoading(true);
      
      // In a real implementation, this would call a backend API to trigger the agent
      // For this demo, we'll simulate the agent running and updating the status
      
      toast.loading(`Running ${nextAgent.name}...`);
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Determine next status based on current status
      let nextStatus;
      switch (content.status.toLowerCase()) {
        case 'draft': nextStatus = 'researched'; break;
        case 'researched': nextStatus = 'written'; break;
        case 'written': nextStatus = 'flow_edited'; break;
        case 'flow_edited': nextStatus = 'line_edited'; break;
        case 'line_edited': nextStatus = 'image_generated'; break;
        case 'image_generated': nextStatus = 'published'; break;
        default: nextStatus = content.status;
      }
      
      // Update content status
      const { data: updatedContent, error: updateError } = await supabase
        .from('content_pieces')
        .update({ 
          status: nextStatus,
          updated_at: new Date().toISOString()
        })
        .eq('id', content.id)
        .select()
        .single();
      
      if (updateError) throw new Error(updateError.message);
      
      // Create agent log
      const { error: logError } = await supabase
        .from('agent_status')
        .insert({
          id: crypto.randomUUID(),
          content_id: content.id,
          agent: nextAgent.agent,
          status: 'completed',
          input: { content_id: content.id },
          output: { status: 'success', message: `Successfully processed content and updated status to ${nextStatus}` },
          created_at: new Date().toISOString()
        });
      
      if (logError) throw new Error(logError.message);
      
      // Update local state
      setContent(updatedContent);
      
      // Refresh agent logs
      const { data: logsData } = await supabase
        .from('agent_status')
        .select('*')
        .eq('content_id', contentId)
        .order('created_at', { ascending: false });
      
      setAgentLogs(logsData || []);
      
      toast.dismiss();
      toast.success(`${nextAgent.name} completed successfully!`);
      
    } catch (err) {
      console.error('Error running agent:', err);
      toast.dismiss();
      toast.error(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setActionLoading(false);
    }
  };
  
  // Function to refresh content data
  const refreshContent = async () => {
    try {
      setActionLoading(true);
      
      // Fetch content piece
      const { data: contentData, error: contentError } = await supabase
        .from('content_pieces')
        .select('*')
        .eq('id', contentId)
        .single();
      
      if (contentError) throw new Error(contentError.message);
      if (!contentData) throw new Error('Content piece not found');
      
      setContent(contentData);
      
      // Fetch agent logs
      const { data: logsData } = await supabase
        .from('agent_status')
        .select('*')
        .eq('content_id', contentId)
        .order('created_at', { ascending: false });
      
      setAgentLogs(logsData || []);
      
      toast.success('Content refreshed');
      
    } catch (err) {
      console.error('Error refreshing content:', err);
      toast.error(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setActionLoading(false);
    }
  };

  // Pipeline steps for visualization
  const pipelineSteps = [
    { status: 'draft', label: 'Draft' },
    { status: 'researched', label: 'Researched' },
    { status: 'written', label: 'Written' },
    { status: 'flow_edited', label: 'Flow Edited' },
    { status: 'line_edited', label: 'Line Edited' },
    { status: 'image_generated', label: 'Image Generated' },
    { status: 'published', label: 'Published' }
  ];
  
  // Get current step index
  const getCurrentStepIndex = () => {
    if (!content) return -1;
    return pipelineSteps.findIndex(step => step.status === content.status);
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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Content Details</h1>
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
      
      {/* Content details */}
      {!loading && !error && content && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main content area */}
          <div className="lg:col-span-3 space-y-6">
            {/* Content header */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">{content.title}</h2>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(content.status)}`}>
                  <span className="mr-1.5">{getStatusIcon(content.status)}</span>
                  {formatStatus(content.status)}
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-300">
                <div>
                  <p><span className="font-medium">Created:</span> {format(new Date(content.created_at), 'MMM d, yyyy h:mm a')}</p>
                  {content.updated_at && (
                    <p><span className="font-medium">Last Updated:</span> {format(new Date(content.updated_at), 'MMM d, yyyy h:mm a')}</p>
                  )}
                </div>
                <div>
                  <p><span className="font-medium">Slug:</span> {content.slug}</p>
                  {content.published_at && (
                    <p><span className="font-medium">Published:</span> {format(new Date(content.published_at), 'MMM d, yyyy h:mm a')}</p>
                  )}
                </div>
              </div>
              
              {/* WordPress link if published */}
              {content.wordpress_post_url && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <a 
                    href={content.wordpress_post_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    <FiExternalLink className="mr-1.5" />
                    View on WordPress
                  </a>
                </div>
              )}
            </div>
            
            {/* Pipeline progress */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
              <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Pipeline Progress</h3>
              <div className="relative">
                {/* Progress bar */}
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-600 rounded-full"
                    style={{ width: `${((getCurrentStepIndex() + 1) / pipelineSteps.length) * 100}%` }}
                  ></div>
                </div>
                
                {/* Steps */}
                <div className="flex justify-between mt-2">
                  {pipelineSteps.map((step, index) => {
                    const isCompleted = index <= getCurrentStepIndex();
                    const isCurrent = index === getCurrentStepIndex();
                    
                    return (
                      <div key={step.status} className="flex flex-col items-center">
                        <div className={`
                          w-6 h-6 rounded-full flex items-center justify-center text-xs
                          ${isCurrent ? 'bg-blue-600 text-white' : isCompleted ? 'bg-green-500 text-white' : 'bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-300'}
                        `}>
                          {isCompleted ? <FiCheck /> : index + 1}
                        </div>
                        <span className={`
                          text-xs mt-1 hidden sm:block
                          ${isCurrent ? 'text-blue-600 dark:text-blue-400 font-medium' : isCompleted ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'}
                        `}>
                          {step.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
            
            {/* Tabs */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
              {/* Tab navigation */}
              <div className="border-b border-gray-200 dark:border-gray-700">
                <nav className="flex -mb-px">
                  <button
                    onClick={() => setActiveTab('content')}
                    className={`py-4 px-6 inline-flex items-center text-sm font-medium border-b-2 ${
                      activeTab === 'content'
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <FiFileText className="mr-2" />
                    Content
                  </button>
                  <button
                    onClick={() => setActiveTab('keywords')}
                    className={`py-4 px-6 inline-flex items-center text-sm font-medium border-b-2 ${
                      activeTab === 'keywords'
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <FiTag className="mr-2" />
                    Keywords
                  </button>
                  <button
                    onClick={() => setActiveTab('images')}
                    className={`py-4 px-6 inline-flex items-center text-sm font-medium border-b-2 ${
                      activeTab === 'images'
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <FiImage className="mr-2" />
                    Images
                  </button>
                  <button
                    onClick={() => setActiveTab('pipeline')}
                    className={`py-4 px-6 inline-flex items-center text-sm font-medium border-b-2 ${
                      activeTab === 'pipeline'
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <FiActivity className="mr-2" />
                    Pipeline Logs
                  </button>
                </nav>
              </div>
              
              {/* Tab content */}
              <div className="p-6">
                {/* Content tab */}
                {activeTab === 'content' && (
                  <div>
                    {content.draft_text ? (
                      <div className="prose dark:prose-invert max-w-none">
                        <div dangerouslySetInnerHTML={{ __html: content.draft_text }} />
                      </div>
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400 italic">No content available yet.</p>
                    )}
                  </div>
                )}
                
                {/* Keywords tab */}
                {activeTab === 'keywords' && (
                  <div>
                    {keywords ? (
                      <div className="space-y-4">
                        <div>
                          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-2">Focus Keyword</h4>
                          <div className="bg-blue-50 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-4 py-2 rounded-md inline-block">
                            {keywords.focus_keyword}
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-2">Supporting Keywords</h4>
                          <div className="flex flex-wrap gap-2">
                            {keywords.supporting_keywords.map((keyword, index) => (
                              <span 
                                key={index}
                                className="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-1 rounded-md text-sm"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400 italic">No keywords available yet.</p>
                    )}
                  </div>
                )}
                
                {/* Images tab */}
                {activeTab === 'images' && (
                  <div>
                    {image ? (
                      <div className="space-y-4">
                        <h4 className="text-md font-medium text-gray-900 dark:text-white mb-2">Featured Image</h4>
                        <div className="relative h-64 w-full rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                          <Image
                            src={`/api/images?path=${encodeURIComponent(image.file_path)}`}
                            alt={content.title}
                            fill
                            style={{ objectFit: 'cover' }}
                          />
                        </div>
                        
                        {image.metadata && (
                          <div className="mt-4">
                            <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Image Metadata</h5>
                            <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-md overflow-auto">
                              <pre className="text-xs text-gray-800 dark:text-gray-200">
                                {JSON.stringify(image.metadata, null, 2)}
                              </pre>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400 italic">No images available yet.</p>
                    )}
                  </div>
                )}
                
                {/* Pipeline logs tab */}
                {activeTab === 'pipeline' && (
                  <div>
                    {agentLogs.length > 0 ? (
                      <div className="space-y-4">
                        {agentLogs.map((log) => (
                          <div 
                            key={log.id}
                            className="border border-gray-200 dark:border-gray-700 rounded-md overflow-hidden"
                          >
                            <div className={`
                              px-4 py-3 flex items-center justify-between
                              ${log.status === 'completed' ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'}
                            `}>
                              <div className="flex items-center">
                                <span className={`
                                  w-2 h-2 rounded-full mr-2
                                  ${log.status === 'completed' ? 'bg-green-500' : 'bg-red-500'}
                                `}></span>
                                <span className="font-medium text-gray-900 dark:text-white">
                                  {getAgentName(log.agent)}
                                </span>
                              </div>
                              <span className="text-sm text-gray-500 dark:text-gray-400">
                                {format(new Date(log.created_at), 'MMM d, yyyy h:mm a')}
                              </span>
                            </div>
                            <div className="p-4 bg-white dark:bg-gray-800">
                              <div className="mb-2">
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Status:</span>{' '}
                                <span className={log.status === 'completed' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                                  {log.status.charAt(0).toUpperCase() + log.status.slice(1)}
                                </span>
                              </div>
                              
                              {log.output && (
                                <div className="mt-2">
                                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Output:</span>
                                  <div className="mt-1 bg-gray-50 dark:bg-gray-700 p-2 rounded text-sm">
                                    {log.output.message || JSON.stringify(log.output)}
                                  </div>
                                </div>
                              )}
                              
                              {log.error && (
                                <div className="mt-2">
                                  <span className="text-sm font-medium text-red-600 dark:text-red-400">Error:</span>
                                  <div className="mt-1 bg-red-50 dark:bg-red-900/20 p-2 rounded text-sm text-red-700 dark:text-red-300">
                                    {log.error.message || JSON.stringify(log.error)}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400 italic">No pipeline logs available yet.</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Actions card */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
              <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Actions</h3>
              
              <div className="space-y-3">
                {/* Run next agent button */}
                {getNextAgent(content.status) && (
                  <button
                    onClick={runNextAgent}
                    disabled={actionLoading}
                    className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed"
                  >
                    {actionLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <FiPlay className="mr-2" />
                        Run {getNextAgent(content.status)?.name}
                      </>
                    )}
                  </button>
                )}
                
                {/* Refresh button */}
                <button
                  onClick={refreshContent}
                  disabled={actionLoading}
                  className="w-full flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <FiRefreshCw className={`mr-2 ${actionLoading ? 'animate-spin' : ''}`} />
                  Refresh Content
                </button>
                
                {/* Edit button */}
                <Link
                  href={`/content/${content.id}/edit`}
                  className="w-full flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
                >
                  <FiEdit className="mr-2" />
                  Edit Content
                </Link>
                
                {/* View on WordPress button */}
                {content.wordpress_post_url && (
                  <a
                    href={content.wordpress_post_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                  >
                    <FiExternalLink className="mr-2" />
                    View on WordPress
                  </a>
                )}
              </div>
            </div>
            
            {/* Strategic plan info */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
              <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Strategic Plan</h3>
              
              {strategicPlan ? (
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      <span className="font-medium">Domain:</span> {strategicPlan.domain}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      <span className="font-medium">Niche:</span> {strategicPlan.niche}
                    </p>
                    {wordpressSite && (
                      <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-300">
                        <FiGlobe className="mr-1.5 text-gray-500" />
                        <span className="font-medium">WordPress Site:</span> {wordpressSite.domain}
                      </div>
                    )}
                  </div>
                  <Link
                    href={`/plans/${content.strategic_plan_id}`}
                    className="inline-flex items-center text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    View Full Plan
                  </Link>
                </div>
              ) : (
                <Link
                  href={`/plans/${content.strategic_plan_id}`}
                  className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  View Strategic Plan
                </Link>
              )}
            </div>
            
            {/* Related content */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
              <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Related Content</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm">
                Related content will be shown here based on keywords and strategic plan.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
