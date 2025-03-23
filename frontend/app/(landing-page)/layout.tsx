import { Footer } from "@/components/footer";
import { LandingPageHeader } from "@/components/landing-page-header";

export default function Layout(props: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <LandingPageHeader
        items={[
          { title: "Home", href: "/" },
          { title: "Features", href: "/#features" },
          { title: "Pricing", href: "/#pricing" },
          { title: "Github", href: "https://github.com/olivmath/paygo", external: true },
        ]}
      />
      <main className="flex-1">{props.children}</main>
      <Footer
        builtBy="Stack Auth"
        builtByLink="https://stack-auth.com/"
        githubLink="https://github.com/olivmah/paygo"
        twitterLink="https://twitter.com/olivmath_"
        linkedinLink="https://linkedin.com/company/paygo-web3"
      />
    </div>
  );
}
