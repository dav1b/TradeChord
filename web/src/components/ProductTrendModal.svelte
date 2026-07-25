<script lang="ts">
  import ProductTrendChart from './ProductTrendChart.svelte';
  import type { ProductTrendData } from '$lib/utils/productAnalysis';

  export let isOpen = false;
  export let productName = '';
  export let trendData: ProductTrendData[] = [];
  export let onClose: () => void = () => {};

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      onClose();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
  <div class="modal-backdrop" on:click={handleBackdropClick} on:keydown={handleKeydown} role="dialog" aria-modal="true" tabindex="-1">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Product Trend: {productName}</h2>
        <button class="close-button" on:click={onClose} aria-label="Close">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="modal-body">
        {#if trendData.length > 0}
          <ProductTrendChart 
            data={trendData} 
            width={800} 
            height={400} 
          />
        {:else}
          <div class="no-data">No trend data available for this product.</div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
  }

  .modal-content {
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    max-width: 900px;
    width: 100%;
    max-height: 90vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #e5e7eb;
    background: #f9fafb;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #111827;
  }

  .close-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 8px;
    border-radius: 6px;
    color: #6b7280;
    transition: all 0.2s;
  }

  .close-button:hover {
    background: #f3f4f6;
    color: #374151;
  }

  .modal-body {
    padding: 24px;
    overflow: auto;
    flex: 1;
  }

  .no-data {
    text-align: center;
    color: #6b7280;
    font-style: italic;
    padding: 40px;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .modal-backdrop {
      padding: 10px;
    }
    
    .modal-content {
      max-height: 95vh;
    }
    
    .modal-header {
      padding: 16px 20px;
    }
    
    .modal-header h2 {
      font-size: 1.1rem;
    }
    
    .modal-body {
      padding: 20px;
    }
  }
</style>
