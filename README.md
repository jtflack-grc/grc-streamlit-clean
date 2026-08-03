# GRC Streamlit Clean

Small Streamlit GRC demos for **#RUNGRCRaleigh** — GRC Engineering Club (NC) “build in public” work.

These are **teaching toys and conversation starters**, not production systems and not portfolio flagships. The mature public work lives at [jtflack-grc.github.io/portfolio](https://jtflack-grc.github.io/portfolio/).

Shared look: `portfolio_skin.py` (IBM Plex / ink–green tokens aligned with that site) plus `.streamlit/config.toml`. Each Cloud app is a **standalone** entrypoint — sibling multipage links in the sidebar are disabled.

## Live apps

URLs are also listed in [`tools/streamlit_urls.txt`](tools/streamlit_urls.txt) (used by the keepalive Action).

### Risk
| App | Live |
| --- | --- |
| FAIR Risk Calculator | https://jtflack-fair-calculator.streamlit.app/ |
| Enterprise Risk Register | https://jtflack-enterprise-risk-register.streamlit.app/ |
| Risk Assessment & Monte Carlo | https://jtflack-risk-assessment-monte-carlo.streamlit.app/ |
| Risk Treatment Plan Generator | https://jtflack-risk-treatment-plan-generator.streamlit.app/ |

### Compliance & controls
| App | Live |
| --- | --- |
| Compliance Dashboard | https://jtflack-compliance-dashboard.streamlit.app/ |
| Control Gap Analysis | https://jtflack-control-gap-analysis.streamlit.app/ |
| Control Tracker | https://jtflack-control-tracker.streamlit.app/ |
| Control Testing Management | https://jtflack-control-testing-management.streamlit.app/ |
| Exception Tracking System | https://jtflack-exception-tracking-system.streamlit.app/ |
| CSF Maturity Assessment | https://jtflack-csf-maturity-assessment.streamlit.app/ |
| Compliance Calendar | https://jtflack-compliance-calendar.streamlit.app/ |
| Policy Management System | https://jtflack-policy-management-system.streamlit.app/ |

### Vendor / third-party
| App | Live |
| --- | --- |
| Vendor Risk Assessment | https://jtflack-vendor-assessment.streamlit.app/ |
| Third-Party Risk Management | https://jtflack-third-party-risk-management.streamlit.app/ |

### Analytics & ROI
| App | Live |
| --- | --- |
| Analytics Dashboard Enhanced | https://jtflack-analytics-dashboard-enhanced.streamlit.app/ |
| KPI Tracking Dashboard | https://jtflack-kpi-tracking-dashboard.streamlit.app/ |
| ROI Calculator | https://jtflack-roi-calculator.streamlit.app/ |
| Security Metrics Dashboard | https://jtflack-security-metrics-dashboard.streamlit.app/ |

### Awareness, privacy, ops
| App | Live |
| --- | --- |
| Security Awareness Training Tracker | https://jtflack-security-awareness-training-tracker.streamlit.app/ |
| Security Awareness Campaign Manager | https://jtflack-security-awareness-campaign-manager.streamlit.app/ |
| Data Privacy Management | https://jtflack-data-privacy-management.streamlit.app/ |
| Asset Management System | https://jtflack-asset-management-system.streamlit.app/ |
| Audit Management System | https://jtflack-audit-management-system.streamlit.app/ |
| Business Continuity Management | https://jtflack-business-continuity-management.streamlit.app/ |
| Incident Response Management | https://jtflack-incident-response-management.streamlit.app/ |

### Platform-specific (legacy / ERP demos)
| App | Live |
| --- | --- |
| IBM i Security Assessment | https://jtflack-ibm-i-security-assessment.streamlit.app/ |
| IBM i User Management | https://jtflack-ibm-i-user-management.streamlit.app/ |
| Unix/Linux Security Assessment | https://jtflack-unix-linux-security-assessment.streamlit.app/ |
| JD Edwards Security Assessment | https://jtflack-jde-security-assessment.streamlit.app/ |

Supporting modules (no Streamlit UI): `ibm_i_audit_core.py`, `jde_audit_core.py`, `unix_linux_audit_core.py`.

## Local setup

**Prerequisites:** Python 3.10+ recommended, `pip`.

```bash
git clone https://github.com/jtflack-grc/grc-streamlit-clean.git
cd grc-streamlit-clean
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

**Single app**

```bash
streamlit run fair_risk_calculator.py
```

**Local hub** (indexes `pages/` via links on the home screen; Cloud entrypoints do not cross-link)

```bash
streamlit run Home.py
```

Theme and branding load from `.streamlit/config.toml` and `portfolio_skin.py`.

## Repo layout

| Path | Role |
| --- | --- |
| `*_*.py` (root) | Standalone Streamlit apps (Cloud entrypoints) |
| `portfolio_skin.py` | Shared skin + `page_header()` |
| `.streamlit/config.toml` | Theme; `showSidebarNavigation = false` |
| `Home.py` / `pages/` | Optional local multipage hub |
| `tools/streamlit_urls.txt` | Canonical live URL list |
| `tools/keepalive_ping.py` | Ping helper for GitHub Actions |
| `.github/workflows/keepalive.yml` | Scheduled pings (~every 10 hours UTC) |

## Streamlit Cloud notes

- Each live URL is its own Community Cloud app pointed at a root `*.py` file in this repo.
- Free Community Cloud **sleeps** apps after ~12 hours idle. The keepalive workflow hits the URL list on a schedule to reduce cold starts — not an uptime SLA.
- Redeploy / reboot an app in the Streamlit Cloud UI if a push does not pick up.

## What these are (and aren’t)

**Are:** interactive GRC concept demos with sample/mock data, useful for club workshops and LinkedIn build-in-public posts under `#RUNGRCRaleigh`.

**Aren’t:** production GRC platforms, audit-ready systems of record, or replacements for IMPACT!, Legacy Control Lab, Decision-Ready, etc.

## License / credit

Personal learning and club-demo material from [jtflack-grc](https://github.com/jtflack-grc). Brand wordmark “i on GRC” matches the public portfolio site.
