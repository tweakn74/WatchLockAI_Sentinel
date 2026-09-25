import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { Alert } from '../components/ui/Alert';
import { Button } from '../components/ui/Button';

interface ConversationEntry {
  timestamp: string;
  question: string;
  module: string;
  ai_response: string;
  responsive: boolean;
}

interface InstallationData {
  installation_date: string;
  total_questions: number;
  responsive_answers: number;
  responsiveness_ratio: number;
  conversation: ConversationEntry[];
}

const InstallationPage: React.FC = () => {
  const [installationData, setInstallationData] = useState<InstallationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [currentModule, setCurrentModule] = useState('detection');
  const [chatResponse, setChatResponse] = useState('');

  useEffect(() => {
    loadInstallationData();
    const interval = setInterval(loadInstallationData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadInstallationData = async () => {
    try {
      const response = await fetch('/api/installation-conversation');
      if (response.ok) {
        const data = await response.json();
        setInstallationData(data);
        setError(null);
      } else {
        setError('Installation data not available yet');
      }
    } catch (err) {
      setError('Unable to load installation data');
    } finally {
      setLoading(false);
    }
  };

  const askAI = async () => {
    if (!currentQuestion.trim()) return;
    
    setChatResponse('[U+1F914] Asking AI...');
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          module: currentModule,
          question: currentQuestion
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setChatResponse(data.response);
      } else {
        setChatResponse('[FAIL] AI failed to respond');
      }
    } catch (err) {
      setChatResponse('[U+1F4A5] Error communicating with AI');
    }
  };

  const getModuleBadgeColor = (module: string) => {
    const colors = {
      detection: 'bg-red-100 text-red-800',
      response: 'bg-orange-100 text-orange-800',
      forensics: 'bg-blue-100 text-blue-800',
      integration: 'bg-green-100 text-green-800',
      core: 'bg-purple-100 text-purple-800',
    };
    return colors[module as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getResponsivenessStatus = (ratio: number) => {
    if (ratio === 100) return { text: 'PERFECT', color: 'bg-green-100 text-green-800' };
    if (ratio >= 80) return { text: 'GOOD', color: 'bg-blue-100 text-blue-800' };
    if (ratio >= 60) return { text: 'POOR', color: 'bg-yellow-100 text-yellow-800' };
    return { text: 'FAILED', color: 'bg-red-100 text-red-800' };
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-lg">Loading installation data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">WatchLockAI Installation Dashboard</h1>
        <Button onClick={loadInstallationData} variant="outline">
          [RELOAD] Refresh
        </Button>
      </div>

      {error && (
        <Alert>
          <div className="flex items-center">
            <span className="text-yellow-600 mr-2">[WARN]</span>
            <div>
              <p className="font-medium">Installation Data Not Available</p>
              <p className="text-sm text-gray-600">
                Complete the WatchLockAI installation to see AI conversation data here.
              </p>
            </div>
          </div>
        </Alert>
      )}

      {installationData && (
        <Tabs defaultValue="conversation" className="w-full">
          <TabsList>
            <TabsTrigger value="conversation">Installation Conversation</TabsTrigger>
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="chat">Live AI Chat</TabsTrigger>
          </TabsList>

          <TabsContent value="summary" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="p-4">
                <div className="text-2xl font-bold text-blue-600">{installationData.total_questions}</div>
                <div className="text-sm text-gray-600">Questions Asked</div>
              </Card>
              <Card className="p-4">
                <div className="text-2xl font-bold text-green-600">{installationData.responsive_answers}</div>
                <div className="text-sm text-gray-600">AI Responses</div>
              </Card>
              <Card className="p-4">
                <div className="text-2xl font-bold text-purple-600">{installationData.responsiveness_ratio}%</div>
                <div className="text-sm text-gray-600">Responsiveness</div>
              </Card>
              <Card className="p-4">
                <Badge className={getResponsivenessStatus(installationData.responsiveness_ratio).color}>
                  {getResponsivenessStatus(installationData.responsiveness_ratio).text}
                </Badge>
                <div className="text-sm text-gray-600 mt-1">Overall Status</div>
              </Card>
            </div>

            <Alert>
              <div className="flex items-center">
                <span className="text-blue-600 mr-2">[BOT]</span>
                <div>
                  <p className="font-medium">AI Responsiveness Test Results</p>
                  <p className="text-sm text-gray-600">
                    Installation completed on {installationData.installation_date}. 
                    The AI {installationData.responsiveness_ratio === 100 ? 'perfectly' : 'partially'} responded to installation questions.
                  </p>
                </div>
              </div>
            </Alert>
          </TabsContent>

          <TabsContent value="conversation" className="space-y-4">
            <div className="space-y-4">
              {installationData.conversation.map((entry, index) => (
                <Card key={index} className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <Badge className={getModuleBadgeColor(entry.module)}>
                        {entry.module.toUpperCase()}
                      </Badge>
                      <span className="text-sm text-gray-500">{entry.timestamp}</span>
                    </div>
                    <Badge className={entry.responsive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {entry.responsive ? '[x] RESPONDED' : '[FAIL] SILENT'}
                    </Badge>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="font-medium text-gray-800">[U+1F914] Installer Question:</p>
                      <p className="text-gray-700">{entry.question}</p>
                    </div>
                    
                    {entry.ai_response ? (
                      <div className="bg-blue-50 p-3 rounded">
                        <p className="font-medium text-blue-800">[BOT] AI Response:</p>
                        <p className="text-blue-700">{entry.ai_response}</p>
                      </div>
                    ) : (
                      <div className="bg-red-50 p-3 rounded">
                        <p className="font-medium text-red-800">[U+1F507] AI was completely silent!</p>
                      </div>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="chat" className="space-y-4">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">[BOT] Chat with WatchLockAI AI</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Module:
                  </label>
                  <select 
                    value={currentModule}
                    onChange={(e) => setCurrentModule(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="detection">[SEARCH] Detection</option>
                    <option value="response">[SYS] Response</option>
                    <option value="forensics">[U+1F52C] Forensics</option>
                    <option value="integration">[LINK] Integration</option>
                    <option value="security">[SHIELD] Security</option>
                    <option value="core">[BRAIN] Core</option>
                    <option value="ai">[BOT] AI Brain</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ask the AI:
                  </label>
                  <textarea
                    value={currentQuestion}
                    onChange={(e) => setCurrentQuestion(e.target.value)}
                    placeholder="Ask the AI about its capabilities, how it works, or any security questions..."
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows={3}
                  />
                </div>

                <Button onClick={askAI} className="w-full">
                  [MSG] Ask AI
                </Button>

                {chatResponse && (
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="font-medium text-blue-800 mb-2">[BOT] AI Response:</p>
                    <p className="text-blue-700 whitespace-pre-wrap">{chatResponse}</p>
                  </div>
                )}
              </div>
            </Card>

            <Alert>
              <div className="flex items-center">
                <span className="text-green-600 mr-2">[PASS]</span>
                <div>
                  <p className="font-medium">Live AI Interaction</p>
                  <p className="text-sm text-gray-600">
                    This is a live connection to WatchLockAI's AI brain. Ask questions about any security module 
                    and get intelligent, real-time responses. This proves the AI is actually working!
                  </p>
                </div>
              </div>
            </Alert>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};

export default InstallationPage;