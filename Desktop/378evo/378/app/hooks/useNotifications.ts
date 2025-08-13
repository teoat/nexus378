// app/hooks/useNotifications.ts
import { toast } from 'react-hot-toast';

/**
 * This hook provides a centralized access point to the toast notification system.
 * By re-exporting the toast object here, we create a project-specific API.
 * If we ever wanted to switch from 'react-hot-toast' to another library,
 * we would only need to update this one file.
 * 
 * Usage:
 * import { useNotifications } from '../hooks/useNotifications';
 * 
 * const { success, error } = useNotifications();
 * 
 * success('Profile updated!');
 * error('Failed to save.');
 */
export function useNotifications() {
  return toast;
}