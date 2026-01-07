import { useState, useEffect, useRef, createContext, useContext } from 'react';
import { Link } from 'react-router-dom';
import styles from './LandingPage.module.css';

/**
 * Landing Page - VibeKanban Style
 * Clean, minimal design with dark mode support
 */

// Dark mode context
const ThemeContext = createContext<{
  isDark: boolean;
  toggle: () => void;
}>({ isDark: false, toggle: () => {} });

function useTheme() {
  return useContext(ThemeContext);
}

// Scroll animation hook
function useScrollAnimation(threshold = 0.1) {
  const ref = useRef<HTMLElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(element);
        }
      },
      { threshold, rootMargin: '0px 0px -50px 0px' }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [threshold]);

  return { ref, isVisible };
}

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
  const { isDark, toggle } = useTheme();

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
          <button
            className={styles.themeToggle}
            onClick={toggle}
            aria-label="Toggle dark mode"
          >
            {isDark ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="5"/>
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
            )}
          </button>
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
      <path d="M 80 140 L 160 140" className={styles.edge} />
      <path d="M 240 140 L 320 100" className={styles.edge} />
      <path d="M 240 140 L 320 180" className={styles.edge} />
      <path d="M 400 100 L 480 140" className={styles.edge} />
      <path d="M 400 180 L 480 140" className={styles.edgeActive} />
      <path d="M 560 140 L 590 140" className={styles.edge} />

      <circle cx="60" cy="140" r="20" className={styles.nodeStart} />

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

      <circle cx="590" cy="140" r="16" className={styles.nodeEnd} />
    </svg>
  );
}

function TestimonialSection() {
  const { ref, isVisible } = useScrollAnimation();

  return (
    <section
      ref={ref as React.RefObject<HTMLElement>}
      className={`${styles.testimonial} ${isVisible ? styles.animateIn : ''}`}
    >
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
  const { ref, isVisible } = useScrollAnimation();

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
    <section
      id="features"
      ref={ref as React.RefObject<HTMLElement>}
      className={`${styles.featureGrid} ${isVisible ? styles.animateIn : ''}`}
    >
      <h2 className={styles.sectionTitle}>Choose Your Analysis</h2>
      <p className={styles.sectionSubtitle}>
        Everything you need to understand and optimize your processes
      </p>
      <div className={styles.grid}>
        {features.map((feature, i) => (
          <div
            key={i}
            className={styles.gridItem}
            style={{ animationDelay: `${i * 0.05}s` }}
          >
            <span className={styles.gridIcon}>{feature.icon}</span>
            <span className={styles.gridLabel}>{feature.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

// SVG Illustrations for feature sections
function UploadIllustration() {
  return (
    <svg viewBox="0 0 400 300" className={styles.illustration}>
      {/* Upload area */}
      <rect x="50" y="50" width="300" height="200" rx="12" fill="currentColor" opacity="0.05" stroke="currentColor" strokeWidth="2" strokeDasharray="8 4"/>
      {/* File icon */}
      <rect x="150" y="100" width="60" height="80" rx="4" fill="currentColor" opacity="0.1"/>
      <path d="M180 100 L180 120 L200 120 L200 100 Z" fill="currentColor" opacity="0.2"/>
      {/* Upload arrow */}
      <path d="M180 160 L180 130 M165 145 L180 130 L195 145" stroke="currentColor" strokeWidth="3" fill="none" strokeLinecap="round" strokeLinejoin="round" className={styles.uploadArrow}/>
      {/* Text lines */}
      <rect x="120" y="200" width="120" height="8" rx="4" fill="currentColor" opacity="0.15"/>
      <rect x="140" y="220" width="80" height="6" rx="3" fill="currentColor" opacity="0.1"/>
    </svg>
  );
}

function BottleneckIllustration() {
  return (
    <svg viewBox="0 0 400 300" className={styles.illustration}>
      {/* Chart background */}
      <rect x="40" y="40" width="320" height="220" rx="8" fill="currentColor" opacity="0.03"/>
      {/* Grid lines */}
      {[80, 130, 180, 230].map((y) => (
        <line key={y} x1="60" y1={y} x2="340" y2={y} stroke="currentColor" opacity="0.1" strokeDasharray="4 4"/>
      ))}
      {/* Bars */}
      <rect x="80" y="120" width="40" height="110" rx="4" fill="#22c55e" opacity="0.8"/>
      <rect x="140" y="90" width="40" height="140" rx="4" fill="#22c55e" opacity="0.8"/>
      <rect x="200" y="60" width="40" height="170" rx="4" fill="#ef4444" opacity="0.9" className={styles.bottleneckBar}/>
      <rect x="260" y="100" width="40" height="130" rx="4" fill="#22c55e" opacity="0.8"/>
      {/* Warning indicator */}
      <circle cx="220" cy="45" r="12" fill="#ef4444"/>
      <text x="220" y="50" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">!</text>
    </svg>
  );
}

function TeamIllustration() {
  return (
    <svg viewBox="0 0 400 300" className={styles.illustration}>
      {/* Dashboard frame */}
      <rect x="30" y="30" width="340" height="240" rx="12" fill="currentColor" fillOpacity="0.05" stroke="currentColor" strokeWidth="1" strokeOpacity="0.2"/>
      {/* Header bar */}
      <rect x="30" y="30" width="340" height="40" rx="12" fill="currentColor" opacity="0.08"/>
      <circle cx="55" cy="50" r="6" fill="#ef4444" opacity="0.8"/>
      <circle cx="75" cy="50" r="6" fill="#fbbf24" opacity="0.8"/>
      <circle cx="95" cy="50" r="6" fill="#22c55e" opacity="0.8"/>
      {/* Charts */}
      <rect x="50" y="90" width="140" height="80" rx="6" fill="currentColor" opacity="0.08"/>
      <rect x="210" y="90" width="140" height="80" rx="6" fill="currentColor" opacity="0.08"/>
      {/* Mini chart lines */}
      <path d="M70 150 L90 130 L110 140 L130 120 L150 135 L170 115" stroke="#22c55e" strokeWidth="2" fill="none"/>
      {/* User avatars */}
      <circle cx="100" cy="220" r="20" fill="currentColor" opacity="0.15"/>
      <circle cx="160" cy="220" r="20" fill="currentColor" opacity="0.15"/>
      <circle cx="220" cy="220" r="20" fill="currentColor" opacity="0.15"/>
      {/* Sharing arrows */}
      <path d="M130 220 L150 220" stroke="currentColor" opacity="0.3" strokeWidth="2" markerEnd="url(#arrow)"/>
      <path d="M190 220 L210 220" stroke="currentColor" opacity="0.3" strokeWidth="2"/>
    </svg>
  );
}

function FeatureSections() {
  const sections = [
    {
      title: 'Upload and analyze in minutes',
      description: 'Drop your CSV or XES file and watch your process map appear. Our smart column detection identifies case IDs, activities, and timestamps automatically.',
      align: 'left',
      Illustration: UploadIllustration,
    },
    {
      title: 'Find bottlenecks instantly',
      description: 'See exactly where time is being wasted. Our AI highlights problem areas and suggests specific improvements based on your data.',
      align: 'right',
      Illustration: BottleneckIllustration,
    },
    {
      title: 'Share insights with your team',
      description: 'Export beautiful reports, embed interactive dashboards, or collaborate in real-time. Everyone sees the same source of truth.',
      align: 'left',
      Illustration: TeamIllustration,
    },
  ];

  return (
    <div id="how-it-works">
      {sections.map((section, i) => (
        <FeatureSection key={i} {...section} index={i} />
      ))}
    </div>
  );
}

function FeatureSection({ title, description, align, Illustration, index }: {
  title: string;
  description: string;
  align: string;
  Illustration: React.FC;
  index: number;
}) {
  const { ref, isVisible } = useScrollAnimation();

  return (
    <section
      ref={ref as React.RefObject<HTMLElement>}
      className={`${styles.featureSection} ${align === 'right' ? styles.featureSectionAlt : ''} ${isVisible ? styles.animateIn : ''}`}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className={styles.featureText}>
        <h3 className={styles.featureTitle}>{title}</h3>
        <p className={styles.featureDescription}>{description}</p>
      </div>
      <div className={styles.featureImage}>
        <Illustration />
      </div>
    </section>
  );
}

function SocialProof() {
  const { ref, isVisible } = useScrollAnimation();

  const activities = [
    { user: 'alex_dev', action: 'discovered 12 bottlenecks', time: '2 hours ago' },
    { user: 'maria_ops', action: 'reduced cycle time by 34%', time: '5 hours ago' },
    { user: 'john_analyst', action: 'exported BPMN diagram', time: '1 day ago' },
    { user: 'sarah_pm', action: 'found $50k in savings', time: '2 days ago' },
  ];

  return (
    <section
      ref={ref as React.RefObject<HTMLElement>}
      className={`${styles.socialProof} ${isVisible ? styles.animateIn : ''}`}
    >
      <h2 className={styles.sectionTitle}>Stay ahead of the curve</h2>
      <p className={styles.sectionSubtitle}>
        Join hundreds of teams discovering process improvements daily
      </p>
      <div className={styles.activityGrid}>
        {activities.map((activity, i) => (
          <div
            key={i}
            className={styles.activityCard}
            style={{ animationDelay: `${i * 0.1}s` }}
          >
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
  const { ref, isVisible } = useScrollAnimation();

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
    <section
      id="faq"
      ref={ref as React.RefObject<HTMLElement>}
      className={`${styles.faq} ${isVisible ? styles.animateIn : ''}`}
    >
      <h2 className={styles.sectionTitle}>FAQs</h2>
      <p className={styles.sectionSubtitle}>
        Common questions about ProcessMind
      </p>
      <div className={styles.faqList}>
        {faqs.map((faq, i) => (
          <div key={i} className={styles.faqItem}>
            <button
              className={`${styles.faqQuestion} ${openIndex === i ? styles.faqQuestionOpen : ''}`}
              onClick={() => setOpenIndex(openIndex === i ? null : i)}
              aria-expanded={openIndex === i}
            >
              <span>{faq.question}</span>
              <span className={`${styles.faqIcon} ${openIndex === i ? styles.faqIconOpen : ''}`}>
                +
              </span>
            </button>
            <div
              className={`${styles.faqAnswerWrapper} ${openIndex === i ? styles.faqAnswerOpen : ''}`}
            >
              <p className={styles.faqAnswer}>{faq.answer}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function CTASection() {
  const { ref, isVisible } = useScrollAnimation();

  return (
    <section
      ref={ref as React.RefObject<HTMLElement>}
      className={`${styles.cta} ${isVisible ? styles.animateIn : ''}`}
    >
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
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') === 'dark' ||
        (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
    return false;
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggle = () => setIsDark(!isDark);

  return (
    <ThemeContext.Provider value={{ isDark, toggle }}>
      <div className={`${styles.page} ${isDark ? styles.dark : ''}`}>
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
    </ThemeContext.Provider>
  );
}
