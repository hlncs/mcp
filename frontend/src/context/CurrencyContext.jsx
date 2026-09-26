import React, { createContext, useContext, useState, useEffect } from 'react'

const CurrencyContext = createContext()

export const useCurrency = () => {
  const context = useContext(CurrencyContext)
  if (!context) {
    throw new Error('useCurrency must be used within CurrencyProvider')
  }
  return context
}

export const CurrencyProvider = ({ children }) => {
  const [currency, setCurrency] = useState('usd')

  // Load from localStorage on mount
  useEffect(() => {
    const savedCurrency = localStorage.getItem('selectedCurrency')
    if (savedCurrency) {
      setCurrency(savedCurrency)
    }
  }, [])

  // Save to localStorage whenever currency changes
  const handleCurrencyChange = (newCurrency) => {
    setCurrency(newCurrency)
    localStorage.setItem('selectedCurrency', newCurrency)
  }

  const currencyOptions = [
    { value: 'usd', label: 'USD ($)', symbol: '$', name: 'US Dollar' },
    { value: 'eur', label: 'EUR (€)', symbol: '€', name: 'Euro' },
    { value: 'aud', label: 'AUD (A$)', symbol: 'A$', name: 'Australian Dollar' },
    { value: 'jpy', label: 'JPY (¥)', symbol: '¥', name: 'Japanese Yen' },
    { value: 'cad', label: 'CAD (C$)', symbol: 'C$', name: 'Canadian Dollar' },
    { value: 'nzd', label: 'NZD (NZ$)', symbol: 'NZ$', name: 'New Zealand Dollar' },
  ]

  const getCurrencySymbol = (curr = currency) => {
    return currencyOptions.find(c => c.value === curr)?.symbol || '$'
  }

  const getCurrencyLabel = (curr = currency) => {
    return currencyOptions.find(c => c.value === curr)?.label || 'USD ($)'
  }

  const getCurrencyName = (curr = currency) => {
    return currencyOptions.find(c => c.value === curr)?.name || 'US Dollar'
  }

  const value = {
    currency,
    setCurrency: handleCurrencyChange,
    currencyOptions,
    getCurrencySymbol,
    getCurrencyLabel,
    getCurrencyName,
  }

  return (
    <CurrencyContext.Provider value={value}>
      {children}
    </CurrencyContext.Provider>
  )
}