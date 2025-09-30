import { useState } from 'react'
import type { Asset } from '@/types/safetyculture'
import { Button } from '@/components/ui/button'

interface AssetDiscoveryViewProps {
  assets: Asset[]
  onSelectAsset: (selectedAssets: Asset[]) => void
}

export function AssetDiscoveryView({ assets, onSelectAsset }: AssetDiscoveryViewProps) {
  const [selectedAssetIds, setSelectedAssetIds] = useState<Set<string>>(new Set())

  const toggleAsset = (assetId: string) => {
    const newSelected = new Set(selectedAssetIds)
    if (newSelected.has(assetId)) {
      newSelected.delete(assetId)
    } else {
      newSelected.add(assetId)
    }
    setSelectedAssetIds(newSelected)
  }

  const toggleAll = () => {
    if (selectedAssetIds.size === assets.length) {
      setSelectedAssetIds(new Set())
    } else {
      setSelectedAssetIds(new Set(assets.map(a => a.id)))
    }
  }

  const handleProcessSelected = () => {
    const selected = assets.filter(a => selectedAssetIds.has(a.id))
    onSelectAsset(selected)
  }

  const formatDate = (date?: string) => {
    if (!date) return 'Never'
    return new Date(date).toLocaleDateString()
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Asset Discovery</h2>
        {selectedAssetIds.size > 0 && (
          <Button onClick={handleProcessSelected}>
            Process Selected ({selectedAssetIds.size})
          </Button>
        )}
      </div>

      <div className="border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted">
            <tr>
              <th className="w-12 p-4">
                <input
                  type="checkbox"
                  checked={selectedAssetIds.size === assets.length && assets.length > 0}
                  onChange={toggleAll}
                  className="cursor-pointer"
                />
              </th>
              <th className="text-left p-4">Asset Name</th>
              <th className="text-left p-4">Type</th>
              <th className="text-left p-4">Location</th>
              <th className="text-left p-4">Last Inspection</th>
            </tr>
          </thead>
          <tbody>
            {assets.map((asset) => (
              <tr
                key={asset.id}
                className={`border-t hover:bg-muted/50 cursor-pointer transition-colors ${
                  selectedAssetIds.has(asset.id) ? 'bg-muted/30' : ''
                }`}
                onClick={() => toggleAsset(asset.id)}
              >
                <td className="p-4">
                  <input
                    type="checkbox"
                    checked={selectedAssetIds.has(asset.id)}
                    onChange={() => toggleAsset(asset.id)}
                    onClick={(e) => e.stopPropagation()}
                    className="cursor-pointer"
                  />
                </td>
                <td className="p-4 font-medium">{asset.name}</td>
                <td className="p-4">{asset.type}</td>
                <td className="p-4">{asset.location}</td>
                <td className="p-4 text-muted-foreground">
                  {formatDate(asset.lastInspectionDate)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {assets.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          No assets found
        </div>
      )}
    </div>
  )
}