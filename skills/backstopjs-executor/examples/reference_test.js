/**
 * Reference Test Configuration
 * 
 * This is a reference test configuration for BackstopJS visual regression testing.
 * Copy and customize this file for your own tests.
 */

module.exports = {
  id: 'example-reference-test',
  
  viewports: [
    {
      name: 'phone',
      width: 375,
      height: 667
    },
    {
      name: 'tablet',
      width: 768,
      height: 1024
    },
    {
      name: 'desktop',
      width: 1280,
      height: 800
    }
  ],
  
  scenarios: [
    {
      label: 'Homepage',
      url: 'https://example.com',
      delay: 1000,
      hideSelectors: ['.cookie-banner', '.newsletter-popup'],
      removeSelectors: ['.ad-overlay'],
      onReadyScript: 'scripts/wait-for-content.js'
    },
    {
      label: 'Login Page',
      url: 'https://example.com/login',
      delay: 500,
      waitForSelector: '#username'
    },
    {
      label: 'Product Listing',
      url: 'https://example.com/products',
      delay: 2000,
      hideSelectors: ['.floating-cart'],
      viewport: 'tablet'
    }
  ],
  
  paths: {
    bitmaps_reference: 'backstop_data/bitmaps_reference',
    bitmaps_test: 'backstop_data/bitmaps_test',
    html_report: 'backstop_data/html_report',
    ci_report: 'backstop_data/ci_report'
  },
  
  report: ['browser', 'CI'],
  
  engine: 'puppeteer',
  
  engineOptions: {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage'
    ]
  },
  
  asyncCaptureLimit: 1,
  asyncCompareLimit: 5,
  
  debug: false
};
