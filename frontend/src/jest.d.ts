import '@testing-library/jest-dom';
import { vi } from 'vitest';

declare global {
  namespace Vi {
    interface Mock<T = any, Y extends any[] = any> {
      mockResolvedValue: (value: T) => Mock<T, Y>;
      mockRejectedValue: (value: any) => Mock<T, Y>;
    }
  }
}

declare module '@testing-library/jest-dom' {
  interface Matchers<R> {
    toBeInTheDocument(): R;
    toHaveTextContent(text: string | RegExp): R;
  }
}

declare const describe: (name: string, fn: () => void) => void;
declare const it: (name: string, fn: () => void) => void;
declare const expect: any;
declare const beforeEach: (fn: () => void) => void;
declare const jest: {
  fn: () => any;
  mock: (path: string, factory: () => any) => void;
};

export {}; 