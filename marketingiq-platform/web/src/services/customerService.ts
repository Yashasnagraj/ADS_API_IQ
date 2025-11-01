// Customer Service
import { apiClient } from './api';
import { Customer } from '../types';
import { API_ENDPOINTS } from '../config/api';

export const customerService = {
  /**
   * Get all customers
   */
  async getCustomers(): Promise<Customer[]> {
    try {
      const response: any = await apiClient.get(API_ENDPOINTS.CUSTOMERS);
      // Backend returns { customers: [...], total: number }
      return response.customers || [];
    } catch (error) {
      console.error('Error fetching customers:', error);
      return [];
    }
  },

  /**
   * Get customer by ID
   */
  async getCustomerById(customerId: number): Promise<Customer | null> {
    try {
      return await apiClient.get<Customer>(`${API_ENDPOINTS.CUSTOMERS}/${customerId}`);
    } catch (error) {
      console.warn('Customer not found or endpoint unavailable:', error);
      return null;
    }
  },
};
