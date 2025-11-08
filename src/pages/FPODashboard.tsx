import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  useFPO,
  useFPOMembers,
  useCollectivePortfolio,
  useProfitDistributions,
  useFPOInsights
} from '@/hooks/useFPOData';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Users,
  TrendingUp,
  MapPin,
  Phone,
  Calendar,
  DollarSign,
  PieChart,
  AlertCircle
} from 'lucide-react';
import { CollectivePortfolioView } from '@/components/fpo/CollectivePortfolioView';
import { MemberManagement } from '@/components/fpo/MemberManagement';
import { InvestmentUnitsTable } from '@/components/fpo/InvestmentUnitsTable';
import { ProfitDistributionView } from '@/components/fpo/ProfitDistributionView';

/**
 * FPO Dashboard - Main interface for Collective Market Governance
 * Displays portfolio, members, Investment Units, and profit distribution
 */
export default function FPODashboard() {
  const { fpoId } = useParams<{ fpoId: string }>();
  const [currentSeason] = useState('kharif-2025');

  const { data: fpo, isLoading: fpoLoading } = useFPO(fpoId!);
  const { data: members, isLoading: membersLoading } = useFPOMembers(fpoId!);
  const { data: portfolio, isLoading: portfolioLoading } = useCollectivePortfolio(
    fpoId!,
    currentSeason
  );
  const { data: distributions } = useProfitDistributions(fpoId!, portfolio?.id);
  const { data: insights } = useFPOInsights(fpoId!);

  if (fpoLoading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      </div>
    );
  }

  if (!fpo) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold">FPO Not Found</h3>
              <p className="text-muted-foreground">
                The requested FPO could not be found.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            {fpo.name}
            <Badge variant={fpo.status === 'active' ? 'default' : 'secondary'}>
              {fpo.status}
            </Badge>
          </h1>
          <div className="flex items-center gap-4 mt-2 text-muted-foreground">
            <div className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              <span className="text-sm">
                {fpo.village}, {fpo.district}, {fpo.state}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Phone className="w-4 h-4" />
              <span className="text-sm">{fpo.contact_phone}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Total Members
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{fpo.total_members}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {members?.filter(m => m.status === 'active').length || 0} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Total Land Area
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{fpo.total_land_area}</p>
            <p className="text-xs text-muted-foreground mt-1">hectares</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Expected Revenue
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {portfolio?.expected_revenue
                ? `₹${(portfolio.expected_revenue / 100000).toFixed(1)}L`
                : '-'}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {currentSeason}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <PieChart className="w-4 h-4" />
              Portfolio Risk
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {portfolio?.risk_score
                ? `${portfolio.risk_score.toFixed(1)}/10`
                : '-'}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Sharpe Ratio: {portfolio?.sharpe_ratio?.toFixed(2) || '-'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Insights & Recommendations */}
      {insights && insights.recommendations && insights.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">AI Recommendations</CardTitle>
            <CardDescription>
              Powered by KisaanMitra CMGA - Collective Market Governance Agent
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {insights.recommendations.map((rec: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 mt-0.5 text-blue-500" />
                  <span className="text-sm">{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="portfolio" className="space-y-4">
        <TabsList>
          <TabsTrigger value="portfolio">Collective Portfolio</TabsTrigger>
          <TabsTrigger value="members">Members</TabsTrigger>
          <TabsTrigger value="units">Investment Units</TabsTrigger>
          <TabsTrigger value="profits">Profit Distribution</TabsTrigger>
        </TabsList>

        <TabsContent value="portfolio">
          <CollectivePortfolioView
            portfolio={portfolio}
            fpoId={fpoId!}
            season={currentSeason}
            loading={portfolioLoading}
          />
        </TabsContent>

        <TabsContent value="members">
          <MemberManagement
            members={members || []}
            fpoId={fpoId!}
            loading={membersLoading}
          />
        </TabsContent>

        <TabsContent value="units">
          <InvestmentUnitsTable
            members={members || []}
            fpoId={fpoId!}
            loading={membersLoading}
          />
        </TabsContent>

        <TabsContent value="profits">
          <ProfitDistributionView
            distributions={distributions || []}
            portfolio={portfolio}
            fpoId={fpoId!}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
