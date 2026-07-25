import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
	plugins: [sveltekit()],
	resolve: {
		alias: {
			$components: fileURLToPath(new URL('./src/components', import.meta.url))
		}
	},
	ssr: {
		noExternal: ['d3']
	}
});
