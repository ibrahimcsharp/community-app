import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';

import { routes } from './app.routes';
import { authInterceptor } from './auth.interceptor';

// App-wide setup, used once in main.ts.
export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    // withComponentInputBinding: URL parts like ":id" or "?reason=" arrive as component inputs.
    provideRouter(routes, withComponentInputBinding()),
    // Every HTTP call goes through authInterceptor (adds the login token).
    provideHttpClient(withInterceptors([authInterceptor])),
  ],
};
