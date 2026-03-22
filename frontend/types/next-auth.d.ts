import 'next-auth';
import 'next-auth/jwt';

declare module 'next-auth' {
  interface User {
    sub?: string;
  }
  interface Session {
    user: {
      sub?: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
    };
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    sub?: string;
    email?: string | null;
    name?: string | null;
    picture?: string | null;
  }
}
