import React, { useState } from 'react';
import { Badge } from './badge';
import { Card, CardContent, CardHeader, CardTitle } from './Card';
import { Button } from './Button';
import { Search, Filter, ExternalLink } from 'lucide-react';
import { cn } from '../../lib/utils';

interface MitreTactic {
  id: string;
  name: string;
  description: string;
  color: string;
  techniques_count: number;
}

interface MitreTechnique {
  id: string;
  name: string;
  tactic: string;
  description: string;
  platforms: string[];
  data_sources: string[];
  mitigations: string[];
  detection_difficulty: 'Low' | 'Medium' | 'High';
  prevalence: 'Low' | 'Medium' | 'High';
}

interface ThreatMapping {
  technique_id: string;
  threat_count: number;
  last_seen: string;
}

interface MitreAttackMatrixProps {
  tactics: MitreTactic[];
  techniques: MitreTechnique[];
  threatMappings?: ThreatMapping[];
  onTechniqueClick?: (technique: MitreTechnique) => void;
  onTacticClick?: (tactic: MitreTactic) => void;
  showHeatmap?: boolean;
}

const difficultyColors = {
  Low: 'bg-green-100 text-green-800',
  Medium: 'bg-yellow-100 text-yellow-800',
  High: 'bg-red-100 text-red-800'
};

const prevalenceColors = {
  Low: 'bg-blue-100 text-blue-800',
  Medium: 'bg-purple-100 text-purple-800',
  High: 'bg-orange-100 text-orange-800'
};

export function MitreAttackMatrix({
  tactics,
  techniques,
  threatMappings = [],
  onTechniqueClick,
  onTacticClick,
  showHeatmap = true
}: MitreAttackMatrixProps) {
  const [selectedTactic, setSelectedTactic] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTechnique, setSelectedTechnique] = useState<MitreTechnique | null>(null);

  const getThreatMapping = (techniqueId: string) => {
    return threatMappings.find(mapping => mapping.technique_id === techniqueId);
  };

  const getHeatmapIntensity = (techniqueId: string) => {
    const mapping = getThreatMapping(techniqueId);
    if (!mapping || !showHeatmap) return 0;
    
    const maxThreats = Math.max(...(threatMappings || []).map(m => m.threat_count));
    return mapping.threat_count / maxThreats;
  };

  const filteredTechniques = (techniques || []).filter(technique => {
    const matchesSearch = technique.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         technique.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTactic = !selectedTactic || technique.tactic === selectedTactic;
    return matchesSearch && matchesTactic;
  });

  const handleTechniqueClick = (technique: MitreTechnique) => {
    setSelectedTechnique(technique);
    onTechniqueClick?.(technique);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">MITRE ATT&CK Matrix</h2>
          <p className="text-gray-600">Adversarial tactics and techniques mapped to your environment</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline" size="sm">
            <ExternalLink className="w-4 h-4 mr-2" />
            View Full Matrix
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
        <input
          type="text"
          placeholder="Search techniques..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Tactics Overview */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
        {(tactics || []).map((tactic) => {
          const tacticThreatCount = (threatMappings || [])
            .filter(mapping => (techniques || []).find(t => t.id === mapping.technique_id)?.tactic === tactic.name)
            .reduce((sum, mapping) => sum + mapping.threat_count, 0);

          return (
            <div
              key={tactic.id}
              className="cursor-pointer"
              onClick={() => {
                setSelectedTactic(selectedTactic === tactic.name ? null : tactic.name);
                onTacticClick?.(tactic);
              }}
            >
              <Card 
                className={cn(
                  'transition-all duration-200 hover:shadow-md',
                  selectedTactic === tactic.name ? 'ring-2 ring-blue-500' : ''
                )}
              >
              <CardHeader className="p-3">
                <div 
                  className="w-full h-2 rounded-full mb-2"
                  style={{ backgroundColor: tactic.color }}
                />
                <CardTitle className="text-sm font-semibold">{tactic.name}</CardTitle>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{tactic.techniques_count} techniques</span>
                  {showHeatmap && tacticThreatCount > 0 && (
                    <Badge variant="destructive" className="text-xs">
                      {tacticThreatCount}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              </Card>
            </div>
          );
        })}
      </div>

      {/* Techniques Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(filteredTechniques || []).map((technique) => {
          const mapping = getThreatMapping(technique.id);
          const intensity = getHeatmapIntensity(technique.id);
          
          return (
            <div
              key={technique.id}
              className="cursor-pointer"
              onClick={() => handleTechniqueClick(technique)}
            >
              <Card 
                className={cn(
                  'transition-all duration-200 hover:shadow-md relative overflow-hidden',
                  selectedTechnique?.id === technique.id ? 'ring-2 ring-blue-500' : '',
                  showHeatmap && intensity > 0 ? 'border-red-200' : ''
                )}
              >
              {/* Heatmap overlay */}
              {showHeatmap && intensity > 0 && (
                <div 
                  className="absolute inset-0 bg-red-500 opacity-10"
                  style={{ opacity: intensity * 0.3 }}
                />
              )}
              
              <CardHeader className="p-4 relative z-10">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge variant="outline" className="text-xs font-mono">
                        {technique.id}
                      </Badge>
                      {mapping && (
                        <Badge variant="destructive" className="text-xs">
                          {mapping.threat_count} threats
                        </Badge>
                      )}
                    </div>
                    <CardTitle className="text-sm font-semibold mb-2">
                      {technique.name}
                    </CardTitle>
                    <p className="text-xs text-gray-600 line-clamp-2 mb-3">
                      {technique.description}
                    </p>
                    
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <Badge className={cn(difficultyColors[technique.detection_difficulty], 'text-xs')}>
                          {technique.detection_difficulty} Detection
                        </Badge>
                        <Badge className={cn(prevalenceColors[technique.prevalence], 'text-xs')}>
                          {technique.prevalence} Prevalence
                        </Badge>
                      </div>
                      
                      <div className="flex flex-wrap gap-1">
                        {(technique.platforms || []).slice(0, 2).map((platform) => (
                          <Badge key={platform} variant="secondary" className="text-xs">
                            {platform}
                          </Badge>
                        ))}
                        {technique.platforms.length > 2 && (
                          <Badge variant="secondary" className="text-xs">
                            +{technique.platforms.length - 2}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              </Card>
            </div>
          );
        })}
      </div>

      {/* Technique Details Modal */}
      {selectedTechnique && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold">{selectedTechnique.name}</h3>
                  <Badge variant="outline" className="mt-2">{selectedTechnique.id}</Badge>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setSelectedTechnique(null)}
                >
                  x
                </Button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Description</h4>
                  <p className="text-sm text-gray-600">{selectedTechnique.description}</p>
                </div>
                
                <div>
                  <h4 className="font-medium mb-2">Platforms</h4>
                  <div className="flex flex-wrap gap-1">
                    {selectedTechnique.platforms.map((platform) => (
                      <Badge key={platform} variant="secondary">{platform}</Badge>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium mb-2">Data Sources</h4>
                  <div className="flex flex-wrap gap-1">
                    {selectedTechnique.data_sources.map((source) => (
                      <Badge key={source} variant="outline">{source}</Badge>
                    ))}
                  </div>
                </div>
                
                {getThreatMapping(selectedTechnique.id) && (
                  <div>
                    <h4 className="font-medium mb-2">Threat Activity</h4>
                    <div className="bg-red-50 p-3 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">
                          {getThreatMapping(selectedTechnique.id)?.threat_count} threats detected
                        </span>
                        <span className="text-xs text-gray-500">
                          Last seen: {getThreatMapping(selectedTechnique.id)?.last_seen}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}