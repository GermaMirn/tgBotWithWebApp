const path = require('path');

module.exports = {
	'*.{js,ts,vue}': (filenames) => {
		const filtered = filenames.filter(f => 
			!f.includes('eslint.config.') && 
			!f.includes('.lintstagedrc.')
		);
		if (filtered.length === 0) return [];
		// Используем относительные пути от текущей рабочей директории
		const cwd = process.cwd();
		const relativeFiles = filtered.map(f => {
			// Если путь абсолютный, делаем его относительным
			if (path.isAbsolute(f)) {
				return path.relative(cwd, f);
			}
			return f;
		}).filter(f => f); // Убираем пустые пути
		
		if (relativeFiles.length === 0) return [];
		
		// Запускаем ESLint с явным указанием рабочей директории
		return [`cd "${cwd}" && eslint --fix --no-cache --max-warnings=0 ${relativeFiles.join(' ')}`];
	},
};

