import { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './LandingPage.module.css';

/**
 * Landing Page - VibeKanban Style
 * Clean, minimal design with off-white background
 */

function AnnouncementBanner() {
  const announcements = [
    'New: Process Discovery with AI-powered insights',
    'v2.0 Released - 10x faster ingestion',
    'Join 500+ companies using ProcessMind',
  ];

  return (
    <div className={styles.banner}>
      <div className={styles.bannerTrack}>
        {[...announcements, ...announcements].map((text, i) => (
          <span key={i} className={styles.bannerItem}>
            {text}
            <span className={styles.bannerDot}>•</span>
          </span>
        ))}
      </div>
    </div>
  );
}

function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.headerInner}>
        <Link to="/" className={styles.logo}>
          ProcessMind
        </Link>

        <nav className={styles.nav}>
          <a href="#features" className={styles.navLink}>Features</a>
          <span className={styles.navDivider}>|</span>
          <a href="#how-it-works" className={styles.navLink}>How It Works</a>
          <span className={styles.navDivider}>|</span>
          <a href="#faq" className={styles.navLink}>FAQ</a>
        </nav>

        <div className={styles.headerActions}>
          <a href="https://github.com" className={styles.githubBadge}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            <span>Star</span>
          </a>
          <Link to="/workspace" className={styles.btnPrimary}>
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}

function HeroSection() {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText('npx create-processmind@latest');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className={styles.hero}>
      <div className={styles.heroContent}>
        <h1 className={styles.heroTitle}>
          Understand your processes with{' '}
          <span className={styles.heroHighlight}>ProcessMind</span>
        </h1>
        <p className={styles.heroSubtitle}>
          Upload your event logs and discover bottlenecks, inefficiencies, and optimization
          opportunities in minutes. No PhD required.
        </p>

        <div className={styles.heroInstall}>
          <code className={styles.installCode}>
            <span className={styles.installPrompt}>$</span>
            npx create-processmind@latest
          </code>
          <button
            className={styles.installCopy}
            onClick={handleCopy}
            title="Copy to clipboard"
          >
            {copied ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
            )}
          </button>
        </div>
      </div>

      <div className={styles.heroDemo}>
        <div className={styles.demoWindow}>
          <div className={styles.demoToolbar}>
            <div className={styles.demoDot} />
            <div className={styles.demoDot} />
            <div className={styles.demoDot} />
          </div>
          <div className={styles.demoContent}>
            <ProcessMapDemo />
          </div>
          <Link to="/workspace" className={styles.demoPlayButton}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
          </Link>
        </div>
      </div>
    </section>
  );
}

function ProcessMapDemo() {
  return (
    <svg viewBox="0 0 600 280" className={styles.processMap}>
      {/* Edges */}
      <path d="M 80 140 L 160 140" className={styles.edge} />
      <path d="M 240 140 L 320 100" className={styles.edge} />
      <path d="M 240 140 L 320 180" className={styles.edge} />
      <path d="M 400 100 L 480 140" className={styles.edge} />
      <path d="M 400 180 L 480 140" className={styles.edgeActive} />
      <path d="M 560 140 L 590 140" className={styles.edge} />

      {/* Start node */}
      <circle cx="60" cy="140" r="20" className={styles.nodeStart} />

      {/* Activity nodes */}
      <g className={styles.node}>
        <rect x="160" y="115" width="80" height="50" rx="4" />
        <text x="200" y="137" className={styles.nodeLabel}>Receive</text>
        <text x="200" y="152" className={styles.nodeCount}>1,247</text>
      </g>

      <g className={styles.node}>
        <rect x="320" y="75" width="80" height="50" rx="4" />
        <text x="360" y="97" className={styles.nodeLabel}>Validate</text>
        <text x="360" y="112" className={styles.nodeCount}>1,189</text>
      </g>

      <g className={styles.nodeActive}>
        <rect x="320" y="155" width="80" height="50" rx="4" />
        <text x="360" y="177" className={styles.nodeLabel}>Process</text>
        <text x="360" y="192" className={styles.nodeCount}>982</text>
      </g>

      <g className={styles.node}>
        <rect x="480" y="115" width="80" height="50" rx="4" />
        <text x="520" y="137" className={styles.nodeLabel}>Complete</text>
        <text x="520" y="152" className={styles.nodeCount}>956</text>
      </g>

      {/* End node */}
      <circle cx="590" cy="140" r="16" className={styles.nodeEnd} />
    </svg>
  );
}

function TestimonialSection() {
  return (
    <section className={styles.testimonial}>
      <blockquote className={styles.testimonialQuote}>
        "ProcessMind helped us identify a bottleneck that was costing us $2M annually.
        We fixed it in two weeks."
      </blockquote>
      <div className={styles.testimonialAuthor}>
        <div className={styles.testimonialAvatar}>SC</div>
        <div>
          <p className={styles.testimonialName}>Sarah Chen</p>
          <p className={styles.testimonialRole}>VP Operations, TechCorp</p>
        </div>
      </div>
    </section>
  );
}

function FeatureGrid() {
  const features = [
    { icon: '📊', label: 'Process Discovery' },
    { icon: '🔍', label: 'Bottleneck Detection' },
    { icon: '📈', label: 'Variant Analysis' },
    { icon: '✅', label: 'Conformance Check' },
    { icon: '🤖', label: 'AI Predictions' },
    { icon: '⚡', label: 'Real-time Monitoring' },
    { icon: '📁', label: 'CSV & XES Import' },
    { icon: '🔗', label: 'API Integration' },
    { icon: '📤', label: 'BPMN Export' },
  ];

  return (
    <section id="features" className={styles.featureGrid}>
      <h2 className={styles.sectionTitle}>Choose Your Analysis</h2>
      <p className={styles.sectionSubtitle}>
        Everything you need to understand and optimize your processes
      </p>
      <div className={styles.grid}>
        {features.map((feature, i) => (
          <div key={i} className={styles.gridItem}>
            <span className={styles.gridIcon}>{feature.icon}</span>
            <span className={styles.gridLabel}>{feature.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function FeatureSections() {
  const sections = [
    {
      title: 'Upload and analyze in minutes',
      description: 'Drop your CSV or XES file and watch your process map appear. Our smart column detection identifies case IDs, activities, and timestamps automatically.',
      align: 'left',
    },
    {
      title: 'Find bottlenecks instantly',
      description: 'See exactly where time is being wasted. Our AI highlights problem areas and suggests specific improvements based on your data.',
      align: 'right',
    },
    {
      title: 'Share insights with your team',
      description: 'Export beautiful reports, embed interactive dashboards, or collaborate in real-time. Everyone sees the same source of truth.',
      align: 'left',
    },
  ];

  return (
    <div id="how-it-works">
      {sections.map((section, i) => (
        <section
          key={i}
          className={`${styles.featureSection} ${section.align === 'right' ? styles.featureSectionAlt : ''}`}
        >
          <div className={styles.featureText}>
            <h3 className={styles.featureTitle}>{section.title}</h3>
            <p className={styles.featureDescription}>{section.description}</p>
          </div>
          <div className={styles.featureImage}>
            <div className={styles.featurePlaceholder}>
              <span>{i + 1}</span>
            </div>
          </div>
        </section>
      ))}
    </div>
  );
}

function SocialProof() {
  const activities = [
    { user: 'alex_dev', action: 'discovered 12 bottlenecks', time: '2 hours ago' },
    { user: 'maria_ops', action: 'reduced cycle time by 34%', time: '5 hours ago' },
    { user: 'john_analyst', action: 'exported BPMN diagram', time: '1 day ago' },
    { user: 'sarah_pm', action: 'found $50k in savings', time: '2 days ago' },
  ];

  return (
    <section className={styles.socialProof}>
      <h2 className={styles.sectionTitle}>Stay ahead of the curve</h2>
      <p className={styles.sectionSubtitle}>
        Join hundreds of teams discovering process improvements daily
      </p>
      <div className={styles.activityGrid}>
        {activities.map((activity, i) => (
          <div key={i} className={styles.activityCard}>
            <div className={styles.activityAvatar}>
              {activity.user.slice(0, 2).toUpperCase()}
            </div>
            <div className={styles.activityContent}>
              <p className={styles.activityUser}>@{activity.user}</p>
              <p className={styles.activityAction}>{activity.action}</p>
            </div>
            <span className={styles.activityTime}>{activity.time}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const faqs = [
    {
      question: 'What data formats do you support?',
      answer: 'We support CSV, XES, and JSON formats. Our smart detection automatically identifies your columns and maps them to the right fields.',
    },
    {
      question: 'How long does it take to get started?',
      answer: 'Most users see their first process map within 5 minutes of signing up. Just upload your data and we handle the rest.',
    },
    {
      question: 'Is my data secure?',
      answer: 'Yes. All data is encrypted at rest and in transit. We\'re SOC 2 Type II certified and GDPR compliant.',
    },
    {
      question: 'Can I try before I buy?',
      answer: 'Absolutely. Start with our free tier - no credit card required. Upgrade when you need more.',
    },
    {
      question: 'What integrations do you offer?',
      answer: 'We integrate with SAP, Salesforce, ServiceNow, and 50+ other systems. Custom integrations available for Enterprise.',
    },
  ];

  return (
    <section id="faq" className={styles.faq}>
      <h2 className={styles.sectionTitle}>FAQs</h2>
      <p className={styles.sectionSubtitle}>
        Common questions about ProcessMind
      </p>
      <div className={styles.faqList}>
        {faqs.map((faq, i) => (
          <div key={i} className={styles.faqItem}>
            <button
              className={styles.faqQuestion}
              onClick={() => setOpenIndex(openIndex === i ? null : i)}
            >
              <span>{faq.question}</span>
              <span className={`${styles.faqIcon} ${openIndex === i ? styles.faqIconOpen : ''}`}>
                +
              </span>
            </button>
            {openIndex === i && (
              <p className={styles.faqAnswer}>{faq.answer}</p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section className={styles.cta}>
      <h2 className={styles.ctaTitle}>Ready to understand your processes?</h2>
      <p className={styles.ctaSubtitle}>Start free. No credit card required.</p>
      <div className={styles.ctaInstall}>
        <code className={styles.installCode}>
          <span className={styles.installPrompt}>$</span>
          npx create-processmind@latest
        </code>
      </div>
      <Link to="/workspace" className={`${styles.btnPrimary} ${styles.btnLarge}`}>
        Get Started Free
      </Link>
    </section>
  );
}

function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerInner}>
        <span className={styles.footerCopyright}>
          © 2024 ProcessMind. All rights reserved.
        </span>
        <div className={styles.footerLinks}>
          <a href="#" className={styles.footerLink}>Terms</a>
          <a href="#" className={styles.footerLink}>Privacy</a>
          <a href="#" className={styles.footerLink}>Contact</a>
        </div>
      </div>
    </footer>
  );
}

export default function LandingPage() {
  return (
    <div className={styles.page}>
      <AnnouncementBanner />
      <Header />
      <HeroSection />
      <TestimonialSection />
      <FeatureGrid />
      <FeatureSections />
      <SocialProof />
      <FAQSection />
      <CTASection />
      <Footer />
    </div>
  );
}
