import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { PieChart, TrendingUp, Droplets, Users as UsersIcon, DollarSign } from 'lucide-react';
import type { CollectivePortfolio } from '@/hooks/useFPOData';

interface CollectivePortfolioViewProps {
  portfolio: CollectivePortfolio | null;
  fpoId: string;
  season: string;
  loading: boolean;
}

export function CollectivePortfolioView({
  portfolio,
  fpoId,
  season,
  loading
}: CollectivePortfolioViewProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-64" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      </div>
    );
  }

  if (!portfolio) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-12">
            <PieChart className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Portfolio Yet</h3>
            <p className="text-muted-foreground mb-4">
              Create your first collective crop portfolio to get started with strategic planning.
            </p>
            <Button>
              <TrendingUp className="w-4 h-4 mr-2" />
              Create Portfolio
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const plannedCrops = portfolio.planned_crops as any[] || [];

  return (
    <div className="space-y-6">
      {/* Portfolio Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Collective Crop Portfolio</CardTitle>
              <CardDescription>
                {season} - {portfolio.year}
              </CardDescription>
            </div>
            <Badge variant={portfolio.status === 'approved' ? 'default' : 'secondary'}>
              {portfolio.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Expected Return</p>
              <p className="text-2xl font-bold">
                {((portfolio.expected_revenue || 0) / 100000).toFixed(1)}L
              </p>
              <p className="text-xs text-muted-foreground">₹ Lakhs</p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">Risk Score</p>
              <p className="text-2xl font-bold">{(portfolio.risk_score || 0).toFixed(1)}</p>
              <p className="text-xs text-muted-foreground">out of 10</p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
              <p className="text-2xl font-bold">{(portfolio.sharpe_ratio || 0).toFixed(2)}</p>
              <p className="text-xs text-muted-foreground">risk-adjusted</p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">Diversification</p>
              <p className="text-2xl font-bold">
                {((portfolio.diversification_index || 0) * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-muted-foreground">index</p>
            </div>
          </div>

          {/* Crop Allocations */}
          <div>
            <h4 className="font-semibold mb-4">Crop Allocations</h4>
            <div className="space-y-3">
              {plannedCrops.map((crop: any, idx: number) => (
                <div key={idx} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{
                          backgroundColor: `hsl(${(idx * 360) / plannedCrops.length}, 70%, 50%)`
                        }}
                      />
                      <span className="font-medium">{crop.cropName || crop.name}</span>
                      <Badge variant="outline" className="text-xs">
                        {crop.landArea?.toFixed(1) || crop.area} ha
                      </Badge>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {crop.expectedReturn
                          ? `${(crop.expectedReturn * 100).toFixed(1)}%`
                          : '-'}
                      </p>
                      <p className="text-xs text-muted-foreground">expected return</p>
                    </div>
                  </div>
                  <Progress
                    value={
                      crop.landArea
                        ? (crop.landArea /
                            plannedCrops.reduce(
                              (sum, c) => sum + (c.landArea || c.area || 0),
                              0
                            )) *
                          100
                        : 0
                    }
                    className="h-2"
                  />
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Resource Utilization */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Resource Utilization</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Land
                </span>
                <span className="text-sm font-medium">95%</span>
              </div>
              <Progress value={95} />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm flex items-center gap-2">
                  <Droplets className="w-4 h-4" />
                  Water
                </span>
                <span className="text-sm font-medium">87%</span>
              </div>
              <Progress value={87} />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm flex items-center gap-2">
                  <UsersIcon className="w-4 h-4" />
                  Labor
                </span>
                <span className="text-sm font-medium">78%</span>
              </div>
              <Progress value={78} />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm flex items-center gap-2">
                  <DollarSign className="w-4 h-4" />
                  Budget
                </span>
                <span className="text-sm font-medium">92%</span>
              </div>
              <Progress value={92} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Portfolio Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm text-muted-foreground">Status</span>
              <Badge variant={portfolio.status === 'approved' ? 'default' : 'secondary'}>
                {portfolio.status}
              </Badge>
            </div>

            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm text-muted-foreground">Crops</span>
              <span className="font-medium">{plannedCrops.length} varieties</span>
            </div>

            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm text-muted-foreground">Risk Level</span>
              <Badge
                variant={
                  (portfolio.risk_score || 0) < 3
                    ? 'default'
                    : (portfolio.risk_score || 0) < 7
                    ? 'secondary'
                    : 'destructive'
                }
              >
                {(portfolio.risk_score || 0) < 3
                  ? 'Low'
                  : (portfolio.risk_score || 0) < 7
                  ? 'Medium'
                  : 'High'}
              </Badge>
            </div>

            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-muted-foreground">Optimization Score</span>
              <span className="font-medium text-green-600">
                {portfolio.sharpe_ratio && portfolio.sharpe_ratio > 1
                  ? 'Excellent'
                  : portfolio.sharpe_ratio && portfolio.sharpe_ratio > 0.5
                  ? 'Good'
                  : 'Fair'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
