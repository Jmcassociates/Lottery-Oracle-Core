// core/static/js/app.js - VERSÃO FINAL CORRIGIDA

class LotteryApp {
    constructor() {
        this.selectedState = '';
        this.isLoading = false;
        this.selectedCategory = null;
        this.allGamesData = null;
        this.pollingInterval = null;

        this.elements = {
            mainCard: document.getElementById('main-card'),
            cardDescriptionCategory: document.getElementById('card-description-category'),
            cardDescriptionState: document.getElementById('card-description-state'),
            stateSelect: document.getElementById('state-select'),
            generateButton: document.getElementById('generate-button'),
            categorySelectionView: document.getElementById('category-selection-view'),
            stateSelectionView: document.getElementById('state-selection-view'),
            recommendationView: document.getElementById('recommendation-view'),
            categoryCards: document.querySelectorAll('.category-card'),
            backToCategoriesBtn: document.getElementById('back-to-categories-btn'),
            backToStatesBtn: document.getElementById('back-to-states-btn'),
            stateTitle: document.getElementById('state-title'),
            gameSubtitle: document.getElementById('game-subtitle'),
            gameLogo: document.getElementById('game-logo'),
            gameLogoFallback: document.getElementById('game-logo-fallback'),
            specialFeaturesRow: document.getElementById('special-features-row'),
            specialFeatures: document.getElementById('special-features'),
            gameFrequency: document.getElementById('game-frequency'),
            officialSiteLink: document.getElementById('official-site-link'),
            officialSiteContainer: document.getElementById('official-site-container'),
            digitDescription: document.getElementById('digit-description'),
            placeholderNumbers: document.getElementById('placeholder-numbers'),
            generateSection: document.getElementById('generate-section'),
            generateBtn: document.getElementById('generate-btn'),
            cacheInfo: document.getElementById('cache-info'),
            loadingSection: document.getElementById('loading-section'),
            loadingMessage: document.getElementById('loading-message'),
            resultsSection: document.getElementById('results-section'),
            mainNumbers: document.getElementById('main-numbers'),
            nextDrawDate: document.getElementById('next-draw-date'),
            alternativeNumbers: document.getElementById('alternative-numbers'),
            analysisText: document.getElementById('analysis-text'),
            generateAgainBtn: document.getElementById('generate-again-btn'),
            cacheInfoLocked: document.getElementById('cache-info-locked'),
            loadingScreen: document.getElementById('loading-screen'),
            app: document.getElementById('app'),
            stateInfoAlert: document.getElementById('state-info-alert'),
            activeGamesCount: document.getElementById('active-games-count'),
            pickNotice: document.getElementById('pick-notice'),         
        };

        this.components = {
            stateSelect: new Select(this.elements.stateSelect),
            stateAlert: new Alert(this.elements.stateInfoAlert),
            notification: new Notification(),
            placeholderDisplay: new NumberDisplay(this.elements.placeholderNumbers),
            mainNumbersDisplay: new NumberDisplay(this.elements.mainNumbers),
        };
    }

    async init() {
        this.showLoadingScreen();
        try {
            this.allGamesData = await lotteryDataManager.loadData();
            this.addEventListeners();
            this.showView('categorySelectionView');
        } catch (error) {
            console.error('Failed to initialize app:', error);
            this.components.notification.show('Fatal Error', 'Could not load essential game data.', 'error');
        } finally {
            this.hideLoadingScreen();
        }
    }

    addEventListeners() {
        // O seletor agora busca apenas por <button> dentro de .category-card
        this.elements.categoryCards = document.querySelectorAll('button.category-card:not(.locked)');
        
        this.elements.categoryCards.forEach(card => {
            card.addEventListener('click', () => {
                this.selectedCategory = card.dataset.category;
                const categoryName = card.querySelector('span').textContent;
                Utils.setText(this.elements.cardDescriptionState, `Showing states for ${categoryName}`);

                if (this.selectedCategory === 'PICK') {
                    Utils.show(this.elements.pickNotice);
                } else {
                    Utils.hide(this.elements.pickNotice);
                }

                this.populateStatesForCategory();
                this.showView('stateSelectionView');
            });
        });

        this.elements.backToCategoriesBtn.addEventListener('click', () => {
            this.resetStateSelection();
            Utils.setText(this.elements.cardDescriptionCategory, 'Get recommendations for local lottery games');
            Utils.hide(this.elements.pickNotice);
            this.showView('categorySelectionView');
        });

        this.elements.backToStatesBtn.addEventListener('click', this.handleBackToStates.bind(this));
        this.elements.stateSelect.addEventListener('change', this.handleStateChange.bind(this));
        this.elements.generateButton.addEventListener('click', this.handleGetRecommendations.bind(this));
        this.elements.generateBtn.addEventListener('click', this.handleGenerateRecommendation.bind(this));
        this.elements.generateAgainBtn.addEventListener('click', this.handleGenerateRecommendation.bind(this)); // Adiciona listener para o botão "Generate Again"
    }

    // Restaura a lógica de popular TODOS os estados e a contagem
    populateStatesForCategory() {
        // CORREÇÃO IMPLÍCITA: lotteryDataManager.getStatesForSelect() deve usar this.selectedCategory
        const allStates = lotteryDataManager.getStatesForSelect(this.selectedCategory); 
        this.components.stateSelect.setOptions(allStates);
        this.elements.stateSelect.disabled = false;
        
        const metadata = lotteryDataManager.getMetadata();
        Utils.setText(this.elements.activeGamesCount, `${metadata.active_games} states with active lottery games`);

        this.resetStateSelection();
    }
    
    // Restaura a lógica de checagem do estado selecionado
    handleStateChange(event) {
        this.selectedState = event.target.value;
        this.components.stateAlert.hide();
        
        if (!this.selectedState) {
            this.elements.generateButton.disabled = true;
            this.elements.generateButton.textContent = 'Select a State';
            return;
        }

        const gameForState = lotteryDataManager.getGameForState(this.selectedState, this.selectedCategory);

        if (gameForState) {
            this.elements.generateButton.textContent = 'Get Recommendations';
            this.elements.generateButton.disabled = false;
        } else {
            const stateData = lotteryDataManager.getStateByName(this.selectedState);
            if (stateData) {
                this.components.stateAlert.type = 'no-lottery';
                this.components.stateAlert.show(
                    `No ${this.selectedCategory} game available in ${stateData.name}`,
                    stateData.suggestion || `Please select another state or game category.`,
                    { text: 'Visit thelotter.us', url: 'https://thelotter.us' }
                );
            }
            this.elements.generateButton.textContent = 'Game not Available';
            this.elements.generateButton.disabled = true;
        }
    }

    showView(viewName) {
        const views = ['categorySelectionView', 'stateSelectionView', 'recommendationView'];
        views.forEach(viewId => {
            if (this.elements[viewId]) Utils.hide(this.elements[viewId]);
        });
        if (this.elements[viewName]) Utils.show(this.elements[viewName]);
    }

    resetStateSelection() {
        this.selectedState = '';
        this.elements.stateSelect.value = '';
        this.elements.generateButton.disabled = true;
        this.elements.generateButton.textContent = 'Select a State';
        this.components.stateAlert.hide();
    }

    handleBackToStates() {
        this.showView('stateSelectionView');
    }

    handleGetRecommendations() {
        if (!this.selectedState) return;
        const gameData = lotteryDataManager.getGameForState(this.selectedState, this.selectedCategory);
        if (!gameData) return;

        this.updateStaticGameInfo(gameData);
        // CORREÇÃO: Passa gameData para garantir que o placeholder seja exibido corretamente ao ENTRAR na view.
        this.resetRecommendationState(gameData); 
        this.checkPendingTask(gameData); 
        this.showView('recommendationView');
    }

    async checkPendingTask(gameData) {
        try {
            const response = await fetch(`/get_scrape_result/${gameData.game_key}/`);
            const result = await response.json();
            if (result.status === 'PENDING') {
                Utils.hide(this.elements.generateSection);
                this.components.notification.show(
                    'Generation in Progress', 
                    'Your numbers are still being generated. Please check back in a moment.', 
                    'info', 
                    10000
                );
            }
        } catch (error) {
            console.error("Could not check for pending task:", error);
        }
    }

    async _showLoadingMessages() {
        if (!this.isLoading) return;
        Utils.setText(this.elements.loadingMessage, "Analyzing Historical Data...");
        await Utils.wait(1500);
        if (!this.isLoading) return;
        Utils.setText(this.elements.loadingMessage, "Calculating Probabilities...");
        await Utils.wait(2000);
        if (!this.isLoading) return;
        Utils.setText(this.elements.loadingMessage, "Finalizing Combinations...");
    }

    async handleGenerateRecommendation() {
        if (this.isLoading) return;
        const gameData = lotteryDataManager.getGameForState(this.selectedState, this.selectedCategory);
        if (!gameData) return;

        this.setGeneratingState(true);
        this._showLoadingMessages(); // Inicia a exibição das mensagens sequenciais

        try {
            const response = await fetch(`/start_scrape_task/${gameData.game_key}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': Utils.getCSRFToken() }
            });
            const result = await response.json();

            // Lógica para lidar com a resposta do cache
            if (response.ok && result.source === 'cache') {
                this.components.notification.show('Lucky numbers', 'The probabilities for this game have been calculated. A new recommendation will be available in 24 hours.', 'info');
                this.showRecommendationResults(result);
                return; // Para o fluxo aqui, pois já temos o resultado
            }
            
            if (response.status === 429) {
                this.components.notification.show('Request Blocked', result.message, 'warning');
                this.resetRecommendationState(gameData); // CORREÇÃO: Passa gameData no reset
                return;
            }

            if (result.status === 'PENDING') {
                await this.pollForResult(gameData);
            } else {
                // Caso a tarefa seja muito rápida ou outro status seja retornado
                this.showRecommendationResults(result);
            }
        } catch (error) {
            console.error('Error starting scrape task:', error);
            this.components.notification.show('Error', 'Could not start the generation process.', 'error');
            this.resetRecommendationState(gameData); // CORREÇÃO: Passa gameData no reset
        }
    }
    
    async pollForResult(gameData) {
        if (this.pollingInterval) clearInterval(this.pollingInterval);

        const poll = async () => {
            try {
                const response = await fetch(`/get_scrape_result/${gameData.game_key}/`);
                const result = await response.json();

                if (result.status === 'SUCCESS') {
                    clearInterval(this.pollingInterval);
                    this.showRecommendationResults(result);
                } else if (result.status === 'FAILURE') {
                    clearInterval(this.pollingInterval);
                    this.components.notification.show('Error', result.error, 'error');
                    this.resetRecommendationState(gameData); // CORREÇÃO: Passa gameData no reset
                }
            } catch (error) {
                clearInterval(this.pollingInterval);
                console.error('Polling error:', error);
                this.components.notification.show('Error', 'An error occurred while fetching results.', 'error');
                this.resetRecommendationState(gameData); // CORREÇÃO: Passa gameData no reset
            }
        };
        
        // Inicia o polling a cada 7 segundos (as mensagens de loading são independentes)
        this.pollingInterval = setInterval(poll, 7000);
    }
    
    // CORREÇÃO: Função agora aceita gameData como argumento
    resetRecommendationState(gameData = null) { 
        this.isLoading = false;
        Utils.show(this.elements.generateSection);
        Utils.hide(this.elements.loadingSection);
        Utils.hide(this.elements.resultsSection);

        // CORREÇÃO: Obtém o digitCount do gameData passado ou recalcula
        const currentDigitCount = gameData ? gameData.digit_count : 
            lotteryDataManager.getGameForState(this.selectedState, this.selectedCategory)?.digit_count || 4;
        
        // CORREÇÃO: Garante que os placeholders são exibidos com a lógica especial correta
        this.components.placeholderDisplay.showPlaceholders(currentDigitCount, currentDigitCount); 
        Utils.show(this.elements.placeholderNumbers); // Garante que o container está visível
        
        this.elements.generateBtn.disabled = false;
        this.elements.generateAgainBtn.disabled = false;
        Utils.hide(this.elements.cacheInfoLocked);
    }
    
    setGeneratingState(isGenerating) {
        this.isLoading = isGenerating;
        if (isGenerating) {
            Utils.hide(this.elements.generateSection);
            Utils.show(this.elements.loadingSection);
            Utils.hide(this.elements.resultsSection);
        } else {
            Utils.hide(this.elements.loadingSection);
        }
    }

    showRecommendationResults(resultData) {
        if (!resultData || !resultData.numbers || resultData.numbers.length === 0) {
            console.error("Invalid result data received:", resultData);
            this.components.notification.show('Error', 'Received invalid data from the server.', 'error');
            this.resetRecommendationState();
            return;
        }
        
        this.setGeneratingState(false);
        Utils.hide(this.elements.placeholderNumbers); // Esconde os '?' quando os números reais chegam.
        Utils.show(this.elements.resultsSection);

        const gameData = lotteryDataManager.getGameForState(this.selectedState, this.selectedCategory);
        const digitCount = gameData?.digit_count || 4; // Obtém o digitCount

        // CORREÇÃO: Passa o digitCount para o mainNumbersDisplay
        this.components.mainNumbersDisplay.showNumbers(resultData.numbers[0], true, digitCount);
        
        if (resultData.next_draw_date && resultData.next_draw_date !== "Unavailable") {
            Utils.setText(this.elements.nextDrawDate, `Next Draw: ${resultData.next_draw_date}`);
            Utils.show(this.elements.nextDrawDate);
        } else {
            Utils.hide(this.elements.nextDrawDate);
        }

        Utils.clearContent(this.elements.alternativeNumbers);
        resultData.numbers.slice(1, 6).forEach(alt => {
            const altContainer = Utils.createElement('div', { className: 'alternative-item' });
            const altDisplay = new NumberDisplay(altContainer);
            // CORREÇÃO: Passa o digitCount para as alternativas
            altDisplay.showNumbers(alt, false, digitCount); 
            Utils.appendChild(this.elements.alternativeNumbers, altContainer);
        });

        // Verifica se gameData existe antes de prosseguir
        if (gameData) {
            const mainCombination = resultData.numbers[0];
            const explanation = numberGenerator.generateExplanation(mainCombination, gameData);
            Utils.setText(this.elements.analysisText, explanation);
        }

        const lockedMessage = "The probabilities for this game have been calculated. A new recommendation will be available in 24 hours.";
        this.elements.generateAgainBtn.disabled = true;
        Utils.setText(this.elements.cacheInfoLocked, lockedMessage);
        Utils.show(this.elements.cacheInfoLocked);

        // Trigger upsell modal
        if (window.APP_STATE && !window.APP_STATE.isPro) {
            // Pequeno delay para permitir que o usuário veja os números antes do modal
            setTimeout(() => this.checkAndShowUpsell(), 1500);
        }
    }

    checkAndShowUpsell() {
        // Ensure it only shows once per session
        if (sessionStorage.getItem('upsellShown')) return;
        
        const usageDays = window.APP_STATE.usageDays;
        let targetModalId = null;

        if (usageDays === 1) {
            targetModalId = 'modalDay1';
        } else if (usageDays === 2) {
            targetModalId = 'modalDay2';
        } else if (usageDays >= 3) {
            targetModalId = 'modalDay3Wheel';
            this.initWheelLogic();
        }

        if (targetModalId) {
            const modalElement = document.getElementById(targetModalId);
            if (modalElement) {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
                sessionStorage.setItem('upsellShown', 'true');
            }
        }
    }

    initWheelLogic() {
        const spinBtn = document.getElementById('spin-wheel-btn');
        const wheel = document.getElementById('discount-wheel');
        const modalBody = document.getElementById('wheel-modal-body');
        const resultBody = document.getElementById('wheel-result-body');

        if (!spinBtn || !wheel) return;

        // Remove listener antigo para evitar múltiplos gatilhos se chamado novamente
        const newSpinBtn = spinBtn.cloneNode(true);
        spinBtn.parentNode.replaceChild(newSpinBtn, spinBtn);

        newSpinBtn.addEventListener('click', () => {
            newSpinBtn.disabled = true;
            
            // Lógica para parar na fatia 2 (50% OFF).
            // A fatia 2 está no index 1 (0-based) = 60 graus.
            // Para cair nela, a roda deve parar de forma que 60 graus fique no topo.
            // O topo (ponteiro) está em -90 graus relativo ao centro.
            // Para forçar a parada, giramos algumas voltas completas (ex: 5 * 360 = 1800)
            // e alinhamos o ângulo da fatia 2 para o ponteiro.
            
            // Rotação alvo para parar na fatia de 50% OFF
            const baseSpins = 360 * 5; 
            const targetDegree = baseSpins + 330; // 270 alinha a fatia-2 (60deg skew) perfeitamente ao topo
            
            wheel.style.transform = `rotate(${targetDegree}deg)`;

            // Aguarda a animação de 4 segundos terminar
            setTimeout(() => {
                Utils.hide(modalBody);
                resultBody.classList.remove('d-none');
                
                // Dispara confetes se quiser, usando uma lib levinha ou apenas mostrando o resultado
            }, 4200);
        });
    }
    
    updateStaticGameInfo(gameData) {
        Utils.setText(this.elements.stateTitle, `${this.selectedState} Lottery`);
        Utils.setText(this.elements.gameSubtitle, gameData.game_name);
        
        // CORREÇÃO: Remove a chamada showPlaceholders daqui. Ela foi movida para resetRecommendationState
        // para garantir que seja exibida de forma consistente após o reset, e não apenas na atualização estática.
        
        Utils.setText(this.elements.digitDescription, `${gameData.digit_count} digit combination for ${gameData.game_name}`);
        Utils.setText(this.elements.gameFrequency, gameData.frequency);
        if (gameData.official_site) {
            Utils.setAttribute(this.elements.officialSiteLink, 'href', gameData.official_site);
            Utils.show(this.elements.officialSiteContainer); // Mostra a seção se a URL existir
        } else {
            Utils.hide(this.elements.officialSiteContainer); // Esconde a seção se a URL estiver vazia
        }
        
        if (gameData.logo_url) {
            this.elements.gameLogo.src = gameData.logo_url;
            Utils.show(this.elements.gameLogo);
            Utils.hide(this.elements.gameLogoFallback);
            this.elements.gameLogo.onerror = () => {
                Utils.hide(this.elements.gameLogo);
                Utils.setText(this.elements.gameLogoFallback, gameData.game_name);
                Utils.show(this.elements.gameLogoFallback);
                this.elements.gameLogo.onerror = null;
            };
        } else {
            Utils.hide(this.elements.gameLogo);
            Utils.setText(this.elements.gameLogoFallback, gameData.game_name);
            Utils.show(this.elements.gameLogoFallback);
        }

        try {
            const features = JSON.parse(gameData.special_features.replace(/'/g, '"'));
            if (features && Array.isArray(features) && features.length > 0 && features[0]) {
                Utils.show(this.elements.specialFeaturesRow);
                Utils.clearContent(this.elements.specialFeatures);
                features.forEach(feature => {
                    const badge = Badge.create(feature.replace(/_/g, ' '), 'purple');
                    Utils.appendChild(this.elements.specialFeatures, badge);
                });
            } else {
                Utils.hide(this.elements.specialFeaturesRow);
            }
        } catch(e) {
            Utils.hide(this.elements.specialFeaturesRow);
        }
    }

    showLoadingScreen() {
        Utils.show(this.elements.loadingScreen);
        Utils.hide(this.elements.app);
    }

    hideLoadingScreen() {
        Utils.hide(this.elements.loadingScreen);
        Utils.show(this.elements.app);
    }

    showError(message) {
        this.components.notification.show('Error', message, 'error', 0);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.lotteryApp = new LotteryApp();
    window.lotteryApp.init();
    
    // Initialize Sticky Banner logic
    if (window.APP_STATE && !window.APP_STATE.isPro) {
        const banner = document.getElementById('upsell-banner');
        const closeBtn = document.querySelector('.banner-close-btn');
        
        if (banner && !sessionStorage.getItem('bannerClosed')) {
            // Mostra o banner com um pequeno delay
            setTimeout(() => banner.classList.add('show'), 2000);
            
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    banner.classList.remove('show');
                    sessionStorage.setItem('bannerClosed', 'true');
                });
            }
        }
    }
});