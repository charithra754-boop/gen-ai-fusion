import { render, screen } from '@testing-library/react';
import { LanguageProvider } from '@/hooks/useLanguage';
import { LanguageSelector } from '../LanguageSelector';

describe('LanguageSelector', () => {
  it('renders the language selector', () => {
    render(
      <LanguageProvider>
        <LanguageSelector />
      </LanguageProvider>
    );

    expect(screen.getByText('English')).toBeInTheDocument();
  });
});
