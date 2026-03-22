import NextAuth from 'next-auth';
import type { NextAuthConfig } from 'next-auth';
import type { Session } from 'next-auth';
import type { JWT } from 'next-auth/jwt';
import Google from 'next-auth/providers/google';

const AUTHORIZED_DOMAIN = 'ntub.edu.tw';

const authConfig: NextAuthConfig = {
  providers: [
    Google({
      clientId: process.env.AUTH_GOOGLE_ID,
      clientSecret: process.env.AUTH_GOOGLE_SECRET,
      authorization: {
        params: {
          scope: 'openid email profile',
          hd: AUTHORIZED_DOMAIN,
          prompt: 'select_account',
        },
      },
    }),
  ],
  pages: {
    signIn: '/login',
    error: '/login',
  },
  callbacks: {
    authorized({ auth, request }) {
      const isLoggedIn = !!auth?.user;
      const { pathname } = request.nextUrl;
      if (pathname === '/login' && isLoggedIn) {
        return Response.redirect(new URL('/', process.env.NEXTAUTH_URL ?? 'http://localhost:3000'));
      }
      return true;
    },
    async jwt({ token, account, profile }) {
      if (account?.provider === 'google' && profile) {
        token.sub = (profile as { sub?: string }).sub ?? undefined;
        token.email = (profile as { email?: string }).email ?? undefined;
        token.name = (profile as { name?: string }).name ?? undefined;
        token.picture = (profile as { picture?: string }).picture ?? undefined;
      }
      return token;
    },
    async session({ session, token }: { session: Session; token: JWT }): Promise<Session> {
      if (token.sub && session.user) {
        session.user.sub = token.sub as string;
      }
      return session;
    },
    signIn({ user }) {
      if (!user.email) {
        return '/login?error=AccessDenied';
      }

      const [, domain] = user.email.split('@');
      if (domain?.toLowerCase() !== AUTHORIZED_DOMAIN) {
        return '/login?error=AccessDenied';
      }

      return true;
    },
  },
  session: {
    strategy: 'jwt',
  },
  secret: process.env.AUTH_SECRET,
  trustHost: true,
  debug: true,
};

export const { handlers, auth, signIn, signOut } = NextAuth(authConfig);
