import SignUpForm from "@/components/auth/SignUpForm";

export default async function SignUp() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md rounded-lg mx-2 md:mx-0">
        <SignUpForm urls={{ signIn: "/auth/signin" }} authProviders={[]} />
      </div>
    </div>
  );
}
