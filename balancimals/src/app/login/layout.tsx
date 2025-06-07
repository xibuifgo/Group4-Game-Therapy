// app/feedback/layout.tsx
import React from "react";
import Navbar from "./components/Navbar"; // adjust path to your Navbar
import Footer from "./components/Footer"; // adjust path to your Footer
import styles from "./layout.module.scss"; // optional styling

export default function FeedbackLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className={styles.layoutWrapper}>
      <Navbar />
      <main className={styles.mainContent}>{children}</main>
      <Footer />
    </div>
  );
}
