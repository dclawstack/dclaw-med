import { CTA } from "@/components/CTA";
import { Demo } from "@/components/Demo";
import { Features } from "@/components/Features";
import { Footer } from "@/components/Footer";
import { Hero } from "@/components/Hero";
import { HowItWorks } from "@/components/HowItWorks";
import { Nav } from "@/components/Nav";
import { Problem } from "@/components/Problem";
import { Roadmap } from "@/components/Roadmap";
import { Stack } from "@/components/Stack";

export default function HomePage() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <Problem />
        <Features />
        <HowItWorks />
        <Stack />
        <Demo />
        <Roadmap />
        <CTA />
      </main>
      <Footer />
    </>
  );
}
