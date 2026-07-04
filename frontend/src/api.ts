import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const getSummary  = () => api.get('/summary').then(r => r.data)
export const getDaily    = (start?: string, end?: string) =>
  api.get('/daily', { params: { start, end } }).then(r => r.data)
export const getForecast = () => api.get('/forecast').then(r => r.data)
export const getShifts   = (start?: string, end?: string) =>
  api.get('/shifts', { params: { start, end } }).then(r => r.data)
export const getHourly   = (date?: string) =>
  api.get('/hourly', { params: { date } }).then(r => r.data)