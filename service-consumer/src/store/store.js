// store.js

import Vuex from 'vuex';

export default new Vuex.Store({
    state: {
        backendURL: null,
    },
    mutations: {
        setBackendURL(state, newValue) {
            state.backendURL = newValue;
        },
    },
    actions: {
        updateBackendURL({ commit }, newValue) {
            commit('setBackendURL', newValue);
        },
    },
    getters: {
        getBackendURL: (state) => state.backendURL,
    },
});
