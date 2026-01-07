import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import styles from './LandingPage.module.css';

/**
 * Custom hook for intersection observer animations
 */
function useInView(threshold = 0.1) {
  const ref = useRef<HTMLDivElement>(null);
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.unobserve(element);
        }
      },
      { threshold }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [threshold]);

  return { ref, isInView };
}

/**
 * Landing Page - Professional marketing page for Process Mining SaaS
 * Inspired by VibeKanban's clean dark design language
 */
export default function LandingPage() {
  return (
    <div className={styles.landingPage}>
      <Navigation />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <PreviewSection />
      <TestimonialsSection />
      <PricingSection />
      <FAQSection />
      <CTASection />
      <Footer />
    </div>
  );
}

function Navigation() {
  return (
    <nav className={styles.nav}>
      <div className={styles.navInner}>
        <Link to="/" className={styles.logo}>
          <span className={styles.logoIcon}>P</span>
          ProcessMind
        </Link>

        <div className={styles.navLinks}>
          <a href="#features" className={styles.navLink}>Features</a>
          <a href="#how-it-works" className={styles.navLink}>How It Works</a>
          <a href="#pricing" className={styles.navLink}>Pricing</a>
          <a href="#faq" className={styles.navLink}>FAQ</a>
        </div>

        <div className={styles.navCta}>
          <Link to="/workspace" className={styles.btnSecondary}>
            Log In
          </Link>
          <Link to="/workspace" className={styles.btnPrimary}>
            Start Free Trial
          </Link>
        </div>
      </div>
    </nav>
  );
}

function HeroSection() {
  return (
    <section className={styles.hero}>
      <div className={styles.heroBackground} />
      <div className={styles.heroContent}>
        <div className={styles.heroBadge}>
          <span className={styles.heroBadgeDot} />
          Trusted by 500+ companies worldwide
        </div>

        <h1 className={styles.heroTitle}>
          <span className={styles.heroTitleGradient}>See how your business </span>
          <span className={styles.heroTitleHighlight}>actually works</span>
        </h1>

        <p className={styles.heroDescription}>
          Upload your event logs and discover your real processes in minutes.
          Find bottlenecks, optimize workflows, and take action—all in one afternoon.
        </p>

        <div className={styles.heroCtas}>
          <Link to="/workspace" className={`${styles.btnPrimary} ${styles.btnLarge}`}>
            Start Free Trial
            <span>→</span>
          </Link>
          <a href="#how-it-works" className={`${styles.btnSecondary} ${styles.btnLarge}`}>
            See How It Works
          </a>
        </div>

        <div className={styles.heroStats}>
          <div className={styles.heroStat}>
            <div className={styles.heroStatValue}>15 min</div>
            <div className={styles.heroStatLabel}>Time to First Insight</div>
          </div>
          <div className={styles.heroStat}>
            <div className={styles.heroStatValue}>$21.9B</div>
            <div className={styles.heroStatLabel}>Market Size by 2030</div>
          </div>
          <div className={styles.heroStat}>
            <div className={styles.heroStatValue}>59.4%</div>
            <div className={styles.heroStatLabel}>Industry CAGR</div>
          </div>
        </div>
      </div>
    </section>
  );
}

function FeaturesSection() {
  const { ref, isInView } = useInView(0.1);
  const features = [
    {
      icon: '📊',
      title: 'Process Discovery',
      description: 'Automatically discover your real processes from event logs. Visualize as DFG, Petri Nets, or BPMN diagrams.',
    },
    {
      icon: '🔍',
      title: 'Bottleneck Detection',
      description: 'Identify where time is being wasted. See wait times, delays, and their impact on your business.',
    },
    {
      icon: '📈',
      title: 'Variant Analysis',
      description: 'Discover all the different ways your process actually runs. Find the happy path and the exceptions.',
    },
    {
      icon: '✅',
      title: 'Conformance Checking',
      description: 'Compare how your process should work vs. how it actually works. Identify deviations instantly.',
    },
    {
      icon: '🤖',
      title: 'AI Predictions',
      description: 'Predict next activities and remaining time for running cases. Take proactive action.',
    },
    {
      icon: '⚡',
      title: 'Real-Time Insights',
      description: 'Get instant insights from your data. No setup, no training, no waiting weeks for results.',
    },
  ];

  return (
    <section id="features" className={`${styles.section} ${styles.features}`} ref={ref}>
      <div className={`${styles.sectionHeader} ${isInView ? styles.animateIn : ''}`}>
        <span className={styles.sectionTag}>Features</span>
        <h2 className={styles.sectionTitle}>
          Everything you need to understand your processes
        </h2>
        <p className={styles.sectionDescription}>
          Professional-grade process mining algorithms, packaged in an intuitive interface
          that anyone can use without training.
        </p>
      </div>

      <div className={styles.featuresGrid}>
        {features.map((feature, index) => (
          <div
            key={index}
            className={`${styles.featureCard} ${isInView ? styles.animateIn : ''}`}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className={styles.featureIcon}>{feature.icon}</div>
            <h3 className={styles.featureTitle}>{feature.title}</h3>
            <p className={styles.featureDescription}>{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function HowItWorksSection() {
  const { ref, isInView } = useInView(0.1);
  const steps = [
    {
      number: '1',
      title: 'Upload Your Data',
      description: 'Drop your CSV or XES file. Our smart column detection identifies your case ID, activities, and timestamps automatically.',
    },
    {
      number: '2',
      title: 'Discover Processes',
      description: 'Watch as your process map appears in seconds. Interactive visualization shows every path, variant, and bottleneck.',
    },
    {
      number: '3',
      title: 'Take Action',
      description: 'Identify improvements, share insights with your team, and track progress over time. See ROI in days, not months.',
    },
  ];

  return (
    <section id="how-it-works" className={styles.howItWorks} ref={ref}>
      <div className={`${styles.sectionHeader} ${isInView ? styles.animateIn : ''}`}>
        <span className={styles.sectionTag}>How It Works</span>
        <h2 className={styles.sectionTitle}>
          From data to insights in 15 minutes
        </h2>
        <p className={styles.sectionDescription}>
          No complex setup, no training required. Just upload your data and start discovering.
        </p>
      </div>

      <div className={styles.stepsContainer}>
        {steps.map((step, index) => (
          <div
            key={index}
            className={`${styles.step} ${isInView ? styles.animateIn : ''}`}
            style={{ animationDelay: `${0.2 + index * 0.15}s` }}
          >
            <div className={styles.stepNumber}>{step.number}</div>
            <h3 className={styles.stepTitle}>{step.title}</h3>
            <p className={styles.stepDescription}>{step.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

/**
 * Animated Process Map - Mock DFG visualization
 */
function ProcessMapPreview() {
  const nodes = [
    { id: 'start', label: 'Start', x: 50, y: 120, type: 'start' },
    { id: 'receive', label: 'Receive Order', x: 180, y: 120, frequency: 1247 },
    { id: 'validate', label: 'Validate', x: 320, y: 70, frequency: 1189 },
    { id: 'check', label: 'Check Stock', x: 320, y: 170, frequency: 1058 },
    { id: 'process', label: 'Process Payment', x: 460, y: 120, frequency: 982, bottleneck: true },
    { id: 'ship', label: 'Ship Order', x: 600, y: 120, frequency: 956 },
    { id: 'end', label: 'End', x: 730, y: 120, type: 'end' },
  ];

  const edges = [
    { from: 'start', to: 'receive', value: 1247 },
    { from: 'receive', to: 'validate', value: 1189 },
    { from: 'receive', to: 'check', value: 58 },
    { from: 'validate', to: 'process', value: 982 },
    { from: 'validate', to: 'check', value: 207 },
    { from: 'check', to: 'process', value: 265 },
    { from: 'process', to: 'ship', value: 956 },
    { from: 'process', to: 'validate', value: 26, rework: true },
    { from: 'ship', to: 'end', value: 956 },
  ];

  const getNodePos = (id: string) => nodes.find(n => n.id === id);

  return (
    <div className={styles.processMap}>
      <div className={styles.processMapHeader}>
        <div className={styles.processMapTabs}>
          <button className={`${styles.processMapTab} ${styles.processMapTabActive}`}>DFG</button>
          <button className={styles.processMapTab}>Petri Net</button>
          <button className={styles.processMapTab}>BPMN</button>
        </div>
        <div className={styles.processMapControls}>
          <span className={styles.processMapLegend}>
            <span className={styles.legendDot} style={{ background: '#10b981' }} /> Normal
          </span>
          <span className={styles.processMapLegend}>
            <span className={styles.legendDot} style={{ background: '#ef4444' }} /> Bottleneck
          </span>
        </div>
      </div>
      <svg viewBox="0 0 780 240" className={styles.processMapSvg}>
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="rgba(255,255,255,0.4)" />
          </marker>
          <marker id="arrowheadRework" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
          </marker>
          <linearGradient id="edgeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="rgba(59,130,246,0.6)" />
            <stop offset="100%" stopColor="rgba(139,92,246,0.6)" />
          </linearGradient>
        </defs>

        {/* Edges */}
        {edges.map((edge, i) => {
          const from = getNodePos(edge.from);
          const to = getNodePos(edge.to);
          if (!from || !to) return null;

          const isRework = edge.rework;
          const dx = to.x - from.x;
          const dy = to.y - from.y;
          const midX = (from.x + to.x) / 2;
          const midY = (from.y + to.y) / 2;

          // Curved path for rework loops
          const path = isRework
            ? `M ${from.x + 40} ${from.y} Q ${midX} ${from.y - 60} ${to.x + 40} ${to.y}`
            : `M ${from.x + 40} ${from.y} L ${to.x - 40} ${to.y}`;

          return (
            <g key={i} className={styles.processEdge}>
              <path
                d={path}
                fill="none"
                stroke={isRework ? '#ef4444' : 'url(#edgeGradient)'}
                strokeWidth={Math.max(1, Math.min(edge.value / 300, 4))}
                markerEnd={isRework ? 'url(#arrowheadRework)' : 'url(#arrowhead)'}
                className={styles.edgePath}
                style={{ animationDelay: `${i * 0.15}s` }}
              />
              {!isRework && (
                <text
                  x={midX}
                  y={midY - 8}
                  className={styles.edgeLabel}
                  textAnchor="middle"
                >
                  {edge.value}
                </text>
              )}
            </g>
          );
        })}

        {/* Nodes */}
        {nodes.map((node, i) => (
          <g
            key={node.id}
            className={`${styles.processNode} ${node.bottleneck ? styles.processNodeBottleneck : ''}`}
            style={{ animationDelay: `${i * 0.1}s` }}
          >
            {node.type === 'start' || node.type === 'end' ? (
              <circle
                cx={node.x}
                cy={node.y}
                r={16}
                className={node.type === 'start' ? styles.nodeStart : styles.nodeEnd}
              />
            ) : (
              <>
                <rect
                  x={node.x - 45}
                  y={node.y - 22}
                  width={90}
                  height={44}
                  rx={6}
                  className={node.bottleneck ? styles.nodeBottleneck : styles.nodeNormal}
                />
                <text x={node.x} y={node.y - 4} className={styles.nodeLabel} textAnchor="middle">
                  {node.label}
                </text>
                <text x={node.x} y={node.y + 12} className={styles.nodeFreq} textAnchor="middle">
                  {node.frequency?.toLocaleString()}
                </text>
              </>
            )}
          </g>
        ))}

        {/* Animated flow particles */}
        <circle className={styles.flowParticle} r="3">
          <animateMotion dur="3s" repeatCount="indefinite">
            <mpath href="#mainPath" />
          </animateMotion>
        </circle>
      </svg>
      <div className={styles.processMapFooter}>
        <span>1,247 cases</span>
        <span>6 activities</span>
        <span>Avg: 4.2 days</span>
      </div>
    </div>
  );
}

function PreviewSection() {
  const { ref, isInView } = useInView(0.1);
  const previewFeatures = [
    {
      title: 'Interactive Process Maps',
      description: 'Zoom, pan, and click on any activity or transition to see details.',
    },
    {
      title: 'Multiple Visualizations',
      description: 'Switch between DFG, Petri Net, and BPMN views with one click.',
    },
    {
      title: 'Frequency & Performance',
      description: 'Toggle between frequency heatmaps and performance timing views.',
    },
    {
      title: 'Smart Filtering',
      description: 'Filter by time range, activities, resources, or custom attributes.',
    },
  ];

  return (
    <section className={styles.preview} ref={ref}>
      <div className={`${styles.previewContent} ${isInView ? styles.animateIn : ''}`}>
        <div className={styles.previewText}>
          <span className={styles.sectionTag}>Process Explorer</span>
          <h2 className={styles.sectionTitle}>
            See your processes like never before
          </h2>
          <p className={styles.sectionDescription}>
            Our interactive process explorer lets you dive deep into your operations.
            Every node is clickable, every path is explorable.
          </p>

          <div className={styles.previewFeatures}>
            {previewFeatures.map((feature, index) => (
              <div
                key={index}
                className={styles.previewFeature}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className={styles.previewFeatureIcon}>✓</div>
                <div className={styles.previewFeatureText}>
                  <h4 className={styles.previewFeatureTitle}>{feature.title}</h4>
                  <p className={styles.previewFeatureDesc}>{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.previewImage}>
          <ProcessMapPreview />
        </div>
      </div>
    </section>
  );
}

function TestimonialsSection() {
  const { ref, isInView } = useInView(0.1);
  const testimonials = [
    {
      quote: "We reduced our order processing time by 40% within the first month. The bottleneck analysis showed us exactly where to focus.",
      author: "Sarah Chen",
      role: "VP Operations",
      company: "TechCorp Inc.",
      avatar: "SC",
    },
    {
      quote: "Finally, a process mining tool that doesn't require a PhD to use. Our entire team was up and running in an afternoon.",
      author: "Marcus Johnson",
      role: "Process Analyst",
      company: "FinanceFlow",
      avatar: "MJ",
    },
    {
      quote: "The variant analysis revealed 47 different ways our team was handling tickets. Now we have one standardized process.",
      author: "Jennifer Wu",
      role: "Director of IT",
      company: "GlobalServices",
      avatar: "JW",
    },
  ];

  return (
    <section className={`${styles.section} ${styles.testimonials}`} ref={ref}>
      <div className={`${styles.sectionHeader} ${isInView ? styles.animateIn : ''}`}>
        <span className={styles.sectionTag}>Testimonials</span>
        <h2 className={styles.sectionTitle}>
          Trusted by process-driven teams
        </h2>
        <p className={styles.sectionDescription}>
          See what our customers say about transforming their operations.
        </p>
      </div>

      <div className={styles.testimonialsGrid}>
        {testimonials.map((testimonial, index) => (
          <div
            key={index}
            className={`${styles.testimonialCard} ${isInView ? styles.animateIn : ''}`}
            style={{ animationDelay: `${0.2 + index * 0.1}s` }}
          >
            <p className={styles.testimonialQuote}>"{testimonial.quote}"</p>
            <div className={styles.testimonialAuthor}>
              <div className={styles.testimonialAvatar}>{testimonial.avatar}</div>
              <div className={styles.testimonialInfo}>
                <h4>{testimonial.author}</h4>
                <p>{testimonial.role}, {testimonial.company}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function PricingSection() {
  const { ref, isInView } = useInView(0.1);
  const plans = [
    {
      name: 'Starter',
      description: 'For individuals and small teams getting started.',
      price: '$99',
      period: '/month',
      features: [
        'Up to 100K events',
        '3 projects',
        'DFG visualization',
        'Basic analytics',
        'Email support',
      ],
      popular: false,
    },
    {
      name: 'Professional',
      description: 'For growing teams with serious process needs.',
      price: '$299',
      period: '/month',
      features: [
        'Up to 1M events',
        'Unlimited projects',
        'All visualizations',
        'Advanced analytics',
        'AI predictions',
        'Priority support',
      ],
      popular: true,
    },
    {
      name: 'Enterprise',
      description: 'For large organizations with custom needs.',
      price: 'Custom',
      period: '',
      features: [
        'Unlimited events',
        'Unlimited everything',
        'SSO & SAML',
        'Custom integrations',
        'Dedicated support',
        'SLA guarantee',
      ],
      popular: false,
    },
  ];

  return (
    <section id="pricing" className={`${styles.section} ${styles.pricing}`} ref={ref}>
      <div className={`${styles.sectionHeader} ${isInView ? styles.animateIn : ''}`}>
        <span className={styles.sectionTag}>Pricing</span>
        <h2 className={styles.sectionTitle}>
          Simple, transparent pricing
        </h2>
        <p className={styles.sectionDescription}>
          Start free, upgrade when you need more. No hidden fees.
        </p>
      </div>

      <div className={styles.pricingGrid}>
        {plans.map((plan, index) => (
          <div
            key={index}
            className={`${styles.pricingCard} ${plan.popular ? styles.pricingCardPopular : ''} ${isInView ? styles.animateIn : ''}`}
            style={{ animationDelay: `${0.2 + index * 0.1}s` }}
          >
            {plan.popular && (
              <span className={styles.pricingPopularBadge}>Most Popular</span>
            )}
            <h3 className={styles.pricingName}>{plan.name}</h3>
            <p className={styles.pricingDescription}>{plan.description}</p>
            <div className={styles.pricingPrice}>
              <span className={styles.pricingAmount}>{plan.price}</span>
              <span className={styles.pricingPeriod}>{plan.period}</span>
            </div>
            <ul className={styles.pricingFeatures}>
              {plan.features.map((feature, i) => (
                <li key={i}>
                  <span className={styles.pricingCheck}>✓</span>
                  {feature}
                </li>
              ))}
            </ul>
            <Link
              to="/workspace"
              className={`${plan.popular ? styles.btnPrimary : styles.btnSecondary} ${styles.pricingCardButton}`}
            >
              {plan.name === 'Enterprise' ? 'Contact Sales' : 'Start Free Trial'}
            </Link>
          </div>
        ))}
      </div>
    </section>
  );
}

function FAQSection() {
  const faqs = [
    {
      question: 'What is process mining?',
      answer: 'Process mining is a technique that uses event log data from your IT systems to automatically discover, monitor, and improve your real business processes. Unlike traditional process mapping, it shows you how your processes actually work, not how they should work.',
    },
    {
      question: 'What data formats do you support?',
      answer: 'We support CSV files with any delimiter, XES (IEEE standard for event logs), and OCEL 2.0 for object-centric process mining. Our smart column detection automatically identifies case IDs, activities, and timestamps.',
    },
    {
      question: 'How long does it take to get started?',
      answer: 'Most users see their first process map within 15 minutes of uploading data. No setup, no training, no waiting for consultants. Just upload your data and start discovering.',
    },
    {
      question: 'Is my data secure?',
      answer: 'Yes. We use industry-standard encryption for data in transit and at rest. Your data is stored in SOC 2 compliant infrastructure, and we never share your data with third parties.',
    },
    {
      question: 'Can I try before I buy?',
      answer: 'Absolutely! Start with our free 14-day trial that includes full access to all features. No credit card required. Upload your own data or explore our sample datasets.',
    },
  ];

  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section id="faq" className={styles.section}>
      <div className={styles.sectionHeader}>
        <span className={styles.sectionTag}>FAQ</span>
        <h2 className={styles.sectionTitle}>
          Frequently asked questions
        </h2>
        <p className={styles.sectionDescription}>
          Everything you need to know about ProcessMind.
        </p>
      </div>

      <div className={styles.faq}>
        {faqs.map((faq, index) => (
          <div key={index} className={styles.faqItem}>
            <button
              className={styles.faqQuestion}
              onClick={() => setOpenIndex(openIndex === index ? null : index)}
            >
              {faq.question}
              <span className={`${styles.faqIcon} ${openIndex === index ? styles.faqIconOpen : ''}`}>
                +
              </span>
            </button>
            {openIndex === index && (
              <div className={styles.faqAnswer}>
                {faq.answer}
              </div>
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
      <h2 className={styles.ctaTitle}>
        Ready to see how your business actually works?
      </h2>
      <p className={styles.ctaDescription}>
        Join 500+ companies that use ProcessMind to discover, analyze,
        and optimize their processes.
      </p>
      <div className={styles.ctaButtons}>
        <Link to="/workspace" className={`${styles.btnPrimary} ${styles.btnLarge}`}>
          Start Free Trial
          <span>→</span>
        </Link>
        <a href="mailto:sales@processmind.io" className={`${styles.btnSecondary} ${styles.btnLarge}`}>
          Talk to Sales
        </a>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerInner}>
        <div className={styles.footerTop}>
          <div className={styles.footerBrand}>
            <div className={styles.footerLogo}>
              <span className={styles.logoIcon}>P</span>
              ProcessMind
            </div>
            <p className={styles.footerTagline}>
              Professional process mining made accessible.
              Discover your real processes, find bottlenecks,
              and optimize operations—all in one platform.
            </p>
          </div>

          <div className={styles.footerColumn}>
            <h4>Product</h4>
            <ul>
              <li><a href="#features">Features</a></li>
              <li><a href="#pricing">Pricing</a></li>
              <li><a href="#faq">FAQ</a></li>
              <li><Link to="/workspace">Dashboard</Link></li>
            </ul>
          </div>

          <div className={styles.footerColumn}>
            <h4>Company</h4>
            <ul>
              <li><a href="#about">About Us</a></li>
              <li><a href="#blog">Blog</a></li>
              <li><a href="#careers">Careers</a></li>
              <li><a href="#contact">Contact</a></li>
            </ul>
          </div>

          <div className={styles.footerColumn}>
            <h4>Legal</h4>
            <ul>
              <li><a href="#privacy">Privacy Policy</a></li>
              <li><a href="#terms">Terms of Service</a></li>
              <li><a href="#security">Security</a></li>
              <li><a href="#gdpr">GDPR</a></li>
            </ul>
          </div>
        </div>

        <div className={styles.footerBottom}>
          <p className={styles.footerCopyright}>
            © 2026 ProcessMind. All rights reserved.
          </p>
          <div className={styles.footerSocial}>
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
              𝕏
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
              in
            </a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
              GH
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
