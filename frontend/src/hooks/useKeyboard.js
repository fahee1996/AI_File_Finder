import { useEffect } from "react";

/**
 * Custom hook for keyboard shortcuts
 */
export function useKeyboardShortcut(key, callback, options = {}) {
  const { ctrl = false, shift = false, alt = false } = options;

  useEffect(() => {
    const handler = (event) => {
      // Check if modifiers match
      const ctrlMatch = ctrl
        ? event.ctrlKey || event.metaKey
        : !event.ctrlKey && !event.metaKey;
      const shiftMatch = shift ? event.shiftKey : !event.shiftKey;
      const altMatch = alt ? event.altKey : !event.altKey;

      // Check if key matches (case insensitive)
      const keyMatch = event.key.toLowerCase() === key.toLowerCase();

      if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
        event.preventDefault();
        callback(event);
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [key, callback, ctrl, shift, alt]);
}

/**
 * Multiple shortcuts handler
 */
export function useKeyboardShortcuts(shortcuts) {
  useEffect(() => {
    const handler = (event) => {
      for (const shortcut of shortcuts) {
        const {
          key,
          ctrl = false,
          shift = false,
          alt = false,
          callback,
        } = shortcut;

        const ctrlMatch = ctrl
          ? event.ctrlKey || event.metaKey
          : !event.ctrlKey && !event.metaKey;
        const shiftMatch = shift ? event.shiftKey : !event.shiftKey;
        const altMatch = alt ? event.altKey : !event.altKey;
        const keyMatch = event.key.toLowerCase() === key.toLowerCase();

        if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
          event.preventDefault();
          callback(event);
          break;
        }
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [shortcuts]);
}

export default useKeyboardShortcut;
