import SignInForm from "@/components/auth/SignInForm";

export default function SignIn() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md rounded-lg mx-2 md:mx-0">
        <SignInForm urls={{ signUp: "/auth/signup", forgotPassword: "/auth/forgot-password" }} authProviders={[]} />
      </div>
    </div>
  );
}
