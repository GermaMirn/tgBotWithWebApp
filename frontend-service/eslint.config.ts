import js from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import pluginVue from 'eslint-plugin-vue';

export default [
	{
		files: ['**/*.{js,mjs,cjs,ts,mts,cts,vue}'], plugins: { js }, extends: ['js/recommended'], languageOptions: { globals: globals.browser },
	},
	tseslint.configs.recommended,
	pluginVue.configs['flat/essential'],
	{ files: ['**/*.vue'], languageOptions: { parserOptions: { parser: tseslint.parser } } },
	{
		files: ['eslint.config.ts', 'eslint.config.js', 'eslint.config.mjs'],
		rules: {
			'import/no-extraneous-dependencies': 'off',
			'import/no-unresolved': 'off',
			'quote-props': 'off',
			'quotes': 'off',
			'key-spacing': 'off',
			'object-curly-spacing': 'off',
			'comma-dangle': 'off',
		},
	},
	{
		rules: {
		"semi": "off",
		"no-plusplus": "off",
		"eol-last": "off",
		"max-len": ["error", 150, { "ignoreUrls":true}],
		"no-tabs": "off",
		"no-alert": "off",
		"prefer-destructuring": "off",
		"indent": "off",
		"no-param-reassign": "off"
		}
	}
];
