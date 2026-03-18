 // Lottery Data Manager - Handles lottery data loading and management

/**
 * Lottery Data Manager Class
 */
class LotteryDataManager {
    constructor() {
        this.data = null;
        this.isLoaded = false;
        this.loadingPromise = null;
    }

    /**
     * Load lottery data from JSON file
     * @returns {Promise<Object>}
     */
    async loadData() {
        if (this.isLoaded && this.data) {
            return this.data;
        }

        if (this.loadingPromise) {
            return this.loadingPromise;
        }

        this.loadingPromise = this._fetchData();
        
        try {
            this.data = await this.loadingPromise;
            this.isLoaded = true;
            return this.data;
        } catch (error) {
            console.error('Error loading lottery data:', error);
            this.loadingPromise = null;
            throw error;
        }
    }

    /**
     * Private method to fetch data
     * @returns {Promise<Object>}
     */
    async _fetchData() {
        try {
            let response;
            try {
                response = await fetch('/static/assets/lottery_data.json'); // fallback
               if (!response.ok) throw new Error('api failed');
            } catch (e) {
               response = await fetch('/static/assets/lottery_data.json'); // fallback
            }
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return this._processData(data);
        } catch (error) {
            console.error('Failed to fetch lottery data:', error);
            throw new Error('Failed to load lottery data. Please try again later.');
        }
    }

    /**
     * Process and validate loaded data
     * @param {Object} rawData - Raw data from JSON
     * @returns {Object}
     */
    _processData(rawData) {
        if (!rawData || !rawData.states || !rawData.games) {
            throw new Error('Invalid lottery data format');
        }

        // Sort states alphabetically
        rawData.states.sort((a, b) => a.name.localeCompare(b.name));

        // Add processed metadata
        const activeStates = rawData.states.filter(state => state.has_lottery);
        rawData.metadata = {
            ...rawData.metadata,
            active_games: activeStates.length,
            total_states: rawData.states.length,
            no_lottery_states: rawData.states.filter(state => !state.has_lottery).length
        };

        return rawData;
    }

    /**
     * Get all states
     * @returns {Array}
     */
    getStates() {
        if (!this.data) {
            throw new Error('Data not loaded. Call loadData() first.');
        }
        return this.data.states;
    }

    /**
     * Get states with lottery
     * @returns {Array}
     */
    getStatesWithLottery() {
        return this.getStates().filter(state => state.has_lottery);
    }

    /**
     * Get states without lottery
     * @returns {Array}
     */
    getStatesWithoutLottery() {
        return this.getStates().filter(state => !state.has_lottery);
    }

    /**
     * Get state by name
     * @param {string} stateName - Name of the state
     * @returns {Object|null}
     */
    getStateByName(stateName) {
        if (!this.data) {
            throw new Error('Data not loaded. Call loadData() first.');
        }
        return this.data.states.find(state => state.name === stateName) || null;
    }

    /**
     * Get game data by key
     * @param {string} gameKey - Game key
     * @returns {Object|null}
     */
    getGameByKey(gameKey) {
        if (!this.data) {
            throw new Error('Data not loaded. Call loadData() first.');
        }
        return this.data.games[gameKey] || null;
    }

    /**
     * Get game data for a state and category
     * @param {string} stateName - Name of the state
     * @param {string} category - The selected game category
     * @returns {Object|null}
     */
    getGameForState(stateName, category) {
        const state = this.getStateByName(stateName);
        if (!state || !state.has_lottery || !state.game_keys || state.game_keys.length === 0) {
            return null;
        }

        // Encontra a chave do jogo que corresponde à categoria selecionada
        const gameKey = state.game_keys.find(key => {
            const game = this.getGameByKey(key);
            return game && game.category === category;
        });
        
        return gameKey ? this.getGameByKey(gameKey) : null;
    }

    /**
     * Get metadata
     * @returns {Object}
     */
    getMetadata() {
        if (!this.data) {
            throw new Error('Data not loaded. Call loadData() first.');
        }
        return this.data.metadata;
    }

    /**
     * Check if state has lottery
     * @param {string} stateName - Name of the state
     * @returns {boolean}
     */
    hasLottery(stateName) {
        const state = this.getStateByName(stateName);
        return state ? state.has_lottery : false;
    }

    /**
     * Get suggestion for state without lottery
     * @param {string} stateName - Name of the state
     * @returns {string|null}
     */
    getSuggestionForState(stateName) {
        const state = this.getStateByName(stateName);
        return state && !state.has_lottery ? state.suggestion : null;
    }

    /**
     * Search states by name
     * @param {string} query - Search query
     * @returns {Array}
     */
    searchStates(query) {
        if (!query || !this.data) {
            return this.getStates();
        }

        const lowercaseQuery = query.toLowerCase();
        return this.getStates().filter(state => 
            state.name.toLowerCase().includes(lowercaseQuery)
        );
    }

    /**
     * Get states formatted for select options
     * @returns {Array}
     */
    getStatesForSelect() {
        return this.getStates().map(state => ({
            value: state.name,
            label: state.name,
            // A propriedade 'disabled' foi removida.
            // A verificação de 'has_lottery' agora é tratada no clique do botão em app.js.
            hasLottery: state.has_lottery
        }));
    }

    /**
     * Get game statistics
     * @returns {Object}
     */
    getGameStatistics() {
        if (!this.data) {
            throw new Error('Data not loaded. Call loadData() first.');
        }

        const games = Object.values(this.data.games);
        const gameTypes = {};
        const frequencies = {};

        games.forEach(game => {
            // Count game types
            gameTypes[game.game_type] = (gameTypes[game.game_type] || 0) + 1;
            
            // Count frequencies
            frequencies[game.frequency] = (frequencies[game.frequency] || 0) + 1;
        });

        return {
            totalGames: games.length,
            gameTypes,
            frequencies,
            averageDigits: games.reduce((sum, game) => sum + game.digit_count, 0) / games.length
        };
    }

    /**
     * Validate game data
     * @param {Object} gameData - Game data to validate
     * @returns {boolean}
     */
    validateGameData(gameData) {
        if (!gameData) return false;

        const requiredFields = [
            'game_name',
            'game_type',
            'digit_count',
            'frequency',
            'official_site'
        ];

        return requiredFields.every(field => 
            gameData.hasOwnProperty(field) && gameData[field] !== null && gameData[field] !== ''
        );
    }

    /**
     * Get random game
     * @returns {Object|null}
     */
    getRandomGame() {
        if (!this.data) {
            throw new Error('Data not loaded. Call loadData() first.');
        }

        const games = Object.values(this.data.games);
        if (games.length === 0) return null;

        const randomIndex = Math.floor(Math.random() * games.length);
        return games[randomIndex];
    }

    /**
     * Get games by type
     * @param {string} gameType - Type of game
     * @returns {Array}
     */
    getGamesByType(gameType) {
        if (!this.data) {
            throw new Error('Data not loaded. Call loadData() first.');
        }

        return Object.values(this.data.games).filter(game => 
            game.game_type.toLowerCase() === gameType.toLowerCase()
        );
    }

    /**
     * Get games by digit count
     * @param {number} digitCount - Number of digits
     * @returns {Array}
     */
    getGamesByDigitCount(digitCount) {
        if (!this.data) {
            throw new Error('Data not loaded. Call loadData() first.');
        }

        return Object.values(this.data.games).filter(game => 
            game.digit_count === digitCount
        );
    }

    /**
     * Export data as JSON
     * @returns {string}
     */
    exportData() {
        if (!this.data) {
            throw new Error('Data not loaded. Call loadData() first.');
        }
        return JSON.stringify(this.data, null, 2);
    }

    /**
     * Get data loading status
     * @returns {Object}
     */
    getStatus() {
        return {
            isLoaded: this.isLoaded,
            hasData: !!this.data,
            isLoading: !!this.loadingPromise && !this.isLoaded
        };
    }

    /**
     * Clear loaded data
     */
    clearData() {
        this.data = null;
        this.isLoaded = false;
        this.loadingPromise = null;
    }

    /**
     * Reload data
     * @returns {Promise<Object>}
     */
    async reloadData() {
        this.clearData();
        return this.loadData();
    }
}

/**
 * Number Generator Class
 */
class NumberGenerator {
    constructor() {
        this.history = [];
        this.maxHistory = 100;
    }

    /**
     * Generate a random combination
     * @param {number} digitCount - Number of digits
     * @returns {string}
     */
    generateCombination(digitCount) {
        if (!digitCount || digitCount < 1 || digitCount > 10) {
            throw new Error('Invalid digit count. Must be between 1 and 10.');
        }

        let combination = '';
        for (let i = 0; i < digitCount; i++) {
            combination += Math.floor(Math.random() * 10).toString();
        }

        // Store in history
        this.addToHistory(combination);
        
        return combination;
    }

    /**
     * Generate multiple unique combinations
     * @param {number} digitCount - Number of digits
     * @param {number} count - Number of combinations to generate
     * @returns {Array}
     */
    generateMultipleCombinations(digitCount, count = 5) {
        const combinations = new Set();
        const maxAttempts = count * 10; // Prevent infinite loop
        let attempts = 0;

        while (combinations.size < count && attempts < maxAttempts) {
            const combination = this.generateCombination(digitCount);
            combinations.add(combination);
            attempts++;
        }

        return Array.from(combinations);
    }

    /**
     * Generate combination with pattern
     * @param {number} digitCount - Number of digits
     * @param {string} pattern - Pattern type ('sequential', 'repeated', 'mixed')
     * @returns {string}
     */
    generateWithPattern(digitCount, pattern = 'mixed') {
        switch (pattern) {
            case 'sequential':
                return this.generateSequential(digitCount);
            case 'repeated':
                return this.generateRepeated(digitCount);
            case 'mixed':
            default:
                return this.generateCombination(digitCount);
        }
    }

    /**
     * Generate sequential combination
     * @param {number} digitCount - Number of digits
     * @returns {string}
     */
    generateSequential(digitCount) {
        const startDigit = Math.floor(Math.random() * (10 - digitCount + 1));
        let combination = '';
        
        for (let i = 0; i < digitCount; i++) {
            combination += ((startDigit + i) % 10).toString();
        }
        
        this.addToHistory(combination);
        return combination;
    }

    /**
     * Generate combination with repeated digits
     * @param {number} digitCount - Number of digits
     * @returns {string}
     */
    generateRepeated(digitCount) {
        const digit = Math.floor(Math.random() * 10);
        const combination = digit.toString().repeat(digitCount);
        
        this.addToHistory(combination);
        return combination;
    }

    /**
     * Add combination to history
     * @param {string} combination - Generated combination
     */
    addToHistory(combination) {
        this.history.unshift({
            combination,
            timestamp: new Date(),
            digitCount: combination.length
        });

        // Limit history size
        if (this.history.length > this.maxHistory) {
            this.history = this.history.slice(0, this.maxHistory);
        }
    }

    /**
     * Get generation history
     * @param {number} limit - Number of entries to return
     * @returns {Array}
     */
    getHistory(limit = 10) {
        return this.history.slice(0, limit);
    }

    /**
     * Clear history
     */
    clearHistory() {
        this.history = [];
    }

    /**
     * Get statistics about generated numbers
     * @returns {Object}
     */
    getStatistics() {
        if (this.history.length === 0) {
            return {
                totalGenerated: 0,
                digitDistribution: {},
                patternAnalysis: {}
            };
        }

        const digitDistribution = {};
        const patternAnalysis = {
            sequential: 0,
            repeated: 0,
            mixed: 0
        };

        this.history.forEach(entry => {
            const { combination } = entry;
            
            // Count digit frequency
            combination.split('').forEach(digit => {
                digitDistribution[digit] = (digitDistribution[digit] || 0) + 1;
            });

            // Analyze patterns
            if (this.isSequential(combination)) {
                patternAnalysis.sequential++;
            } else if (this.isRepeated(combination)) {
                patternAnalysis.repeated++;
            } else {
                patternAnalysis.mixed++;
            }
        });

        return {
            totalGenerated: this.history.length,
            digitDistribution,
            patternAnalysis
        };
    }

    /**
     * Check if combination is sequential
     * @param {string} combination - Combination to check
     * @returns {boolean}
     */
    isSequential(combination) {
        const digits = combination.split('').map(Number);
        for (let i = 1; i < digits.length; i++) {
            if ((digits[i] - digits[i-1]) % 10 !== 1 && digits[i] - digits[i-1] !== 1) {
                return false;
            }
        }
        return true;
    }

    /**
     * Check if combination has repeated digits
     * @param {string} combination - Combination to check
     * @returns {boolean}
     */
    isRepeated(combination) {
        const uniqueDigits = new Set(combination.split(''));
        return uniqueDigits.size === 1;
    }

    /**
     * Generate explanation for combination
     * @param {string} combination - Generated combination
     * @param {Object} gameData - Game data
     * @returns {string}
     */
    generateExplanation(combination, gameData) {
        const patterns = [];
        
        if (this.isSequential(combination)) {
            patterns.push('sequential pattern');
        }
        
        if (this.isRepeated(combination)) {
            patterns.push('repeated digits');
        }
        
        const digitSum = combination.split('').reduce((sum, digit) => sum + parseInt(digit), 0);
        const isEvenSum = digitSum % 2 === 0;
        
        let explanation = `Based on ${gameData.game_type} patterns and ${gameData.odds} odds, `;
        
        if (patterns.length > 0) {
            explanation += `this combination features ${patterns.join(' and ')} with `;
        } else {
            explanation += 'this combination offers ';
        }
        
        explanation += `balanced probability distribution for ${gameData.frequency} draws`;
        
        if (isEvenSum) {
            explanation += '. The digit sum is even, which appears in approximately 50% of winning combinations';
        } else {
            explanation += '. The digit sum is odd, providing good statistical balance';
        }
        
        explanation += '.';
        
        return explanation;
    }
}

// Create global instances
const lotteryDataManager = new LotteryDataManager();
const numberGenerator = new NumberGenerator();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        LotteryDataManager,
        NumberGenerator,
        lotteryDataManager,
        numberGenerator
    };
}
