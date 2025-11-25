import js from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import pluginVue from 'eslint-plugin-vue';
import { defineConfig } from 'eslint/config';

export default defineConfig([
	{
		files: ['**/*.{js,mjs,cjs,ts,mts,cts,vue}'], plugins: { js }, extends: ['js/recommended'], languageOptions: { globals: globals.browser },
	},
	tseslint.configs.recommended,
	pluginVue.configs['flat/essential'],
	{ files: ['**/*.vue'], languageOptions: { parserOptions: { parser: tseslint.parser } } },
	{
		rules: {
		"semi": "off",
		"no-plusplus": "off",
		"eol-lasr": "off",
		"max-len": ["error", 150, { "ignoreUrls":true}],
		"no-tabs": "off",
		"no-alert": "off",
		"prefer-destructuring": "off",
		"indent": [2, "tab"],
		"no-param-reassign": "off"
		}
	}
]);
