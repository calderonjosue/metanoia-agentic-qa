// Cypress Executor Examples

describe('Basic Cypress Tests', () => {
  beforeEach(() => {
    cy.visit('https://example.com')
  })

  it('should visit a website', () => {
    cy.visit('https://example.com')
    cy.contains('Example Domain')
  })

  it('should click an element', () => {
    cy.get('#submit-button').click()
  })

  it('should type into an input', () => {
    cy.get('#username').type('testuser')
  })

  it('should find element by text', () => {
    cy.contains('Submit').click()
  })

  it('should get element by selector', () => {
    cy.get('.nav-links').should('be.visible')
  })
})

describe('Form Submission', () => {
  beforeEach(() => {
    cy.visit('https://example.com/form')
  })

  it('should fill and submit a form', () => {
    cy.get('#username').type('testuser')
    cy.get('#password').type('password123')
    cy.get('#submit-button').click()
    cy.contains('Welcome').should('be.visible')
  })
})
