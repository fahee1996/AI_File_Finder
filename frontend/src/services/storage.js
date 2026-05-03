/**
 * Local storage service for persisting data
 */

const STORAGE_KEYS = {
  SEARCH_HISTORY: "ai_file_finder_search_history",
  FAVORITES: "ai_file_finder_favorites",
  RECENT_FILES: "ai_file_finder_recent_files",
};

class StorageService {
  // Search History
  getSearchHistory() {
    try {
      const history = localStorage.getItem(STORAGE_KEYS.SEARCH_HISTORY);
      return history ? JSON.parse(history) : [];
    } catch (error) {
      console.error("Error loading search history:", error);
      return [];
    }
  }

  addToSearchHistory(query) {
    try {
      const history = this.getSearchHistory();

      // Remove duplicates
      const filtered = history.filter((item) => item.query !== query);

      // Add to beginning
      filtered.unshift({
        query,
        timestamp: new Date().toISOString(),
      });

      // Keep only last 50 searches
      const limited = filtered.slice(0, 50);

      localStorage.setItem(
        STORAGE_KEYS.SEARCH_HISTORY,
        JSON.stringify(limited)
      );
      return limited;
    } catch (error) {
      console.error("Error saving search history:", error);
      return [];
    }
  }

  clearSearchHistory() {
    localStorage.removeItem(STORAGE_KEYS.SEARCH_HISTORY);
  }

  // Favorites
  getFavorites() {
    try {
      const favorites = localStorage.getItem(STORAGE_KEYS.FAVORITES);
      return favorites ? JSON.parse(favorites) : [];
    } catch (error) {
      console.error("Error loading favorites:", error);
      return [];
    }
  }

  addToFavorites(file) {
    try {
      const favorites = this.getFavorites();

      // Check if already favorited
      const exists = favorites.some((fav) => fav.path === file.path);
      if (exists) {
        return favorites;
      }

      favorites.unshift({
        ...file,
        favoritedAt: new Date().toISOString(),
      });

      // Keep only 100 favorites
      const limited = favorites.slice(0, 100);

      localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify(limited));
      return limited;
    } catch (error) {
      console.error("Error adding favorite:", error);
      return [];
    }
  }

  removeFromFavorites(filePath) {
    try {
      const favorites = this.getFavorites();
      const filtered = favorites.filter((fav) => fav.path !== filePath);
      localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify(filtered));
      return filtered;
    } catch (error) {
      console.error("Error removing favorite:", error);
      return [];
    }
  }

  isFavorite(filePath) {
    const favorites = this.getFavorites();
    return favorites.some((fav) => fav.path === filePath);
  }

  clearFavorites() {
    localStorage.removeItem(STORAGE_KEYS.FAVORITES);
  }

  // Recent Files
  getRecentFiles() {
    try {
      const recent = localStorage.getItem(STORAGE_KEYS.RECENT_FILES);
      return recent ? JSON.parse(recent) : [];
    } catch (error) {
      console.error("Error loading recent files:", error);
      return [];
    }
  }

  addToRecentFiles(file) {
    try {
      const recent = this.getRecentFiles();

      // Remove duplicates
      const filtered = recent.filter((item) => item.path !== file.path);

      filtered.unshift({
        ...file,
        openedAt: new Date().toISOString(),
      });

      // Keep only last 20
      const limited = filtered.slice(0, 20);

      localStorage.setItem(STORAGE_KEYS.RECENT_FILES, JSON.stringify(limited));
      return limited;
    } catch (error) {
      console.error("Error saving recent file:", error);
      return [];
    }
  }

  clearRecentFiles() {
    localStorage.removeItem(STORAGE_KEYS.RECENT_FILES);
  }
}

export default new StorageService();
