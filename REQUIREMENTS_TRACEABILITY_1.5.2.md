# AskYourDoubt 1.5.2 Requirement Traceability

| Requirement | Implementation | Verification |
|---|---|---|
| Sky-grey or blue commercial palette | Final CSS 1.5.2 override replaces green-led branding with navy, sky-blue, white and cool grey | `test_sky_blue_palette_and_realistic_login_asset`; responsive screenshots |
| Professional compact typography | Existing global compact type hierarchy retained across roles | Core UI contract tests; device matrix |
| Realistic Indian teacher login image | Local `static/img/teacher-login-classroom.jpg` used by `templates/teacher/login.html` | Asset/template regression test |
| Teacher completed pagination | `completed_page` and `completed_per_page` API parameters; 10/20/30 UI pager | 1.5.2 pagination regression test |
| Teacher skipped pagination | `skipped_page` and `skipped_per_page` API parameters; 10/20/30 UI pager | 1.5.2 pagination regression test |
| Student answered pagination | `answered_page` and `answered_per_page` API parameters; 10/20/30 UI pager | 1.5.2 pagination regression test |
| Teacher download Total | CSV filter `ALL`, defined as Open + Completed | Filtered export regression test |
| Teacher download Open | CSV filter `OPEN` | Filtered export regression test |
| Teacher download Completed | CSV filter `COMPLETED` | Filtered export regression test |
| Teacher download Skipped | CSV filter `SKIPPED` | Filtered export regression test |
| QR/link full page | Existing full QR route with Back to Session plus browser-fullscreen target on QR card | Template contract test and device render |
| Silent one-second update | Existing in-flight guarded 1000 ms polling retained | Existing functional/UI contracts |
| Minimize/maximize live doubt areas | Existing teacher/student focus controls retained | Existing functional/UI contracts |
| File-selection visibility | Existing filename/size/remove state retained | Existing 1.5.1 regression tests |
| Completed question text visible | Existing teacher and student renderers retained | Existing 1.5.1 regression tests |
| Session-wise teacher Question Bank | Existing 1.5.1 session filter retained | Existing 1.5.1 regression tests |
| Phone/tablet/laptop responsiveness | 12 profiles × 14 pages | 168/168 device matrix |
| Chrome/Firefox/WebKit CI configuration | GitHub workflows and Playwright matrix retained | YAML parsing PASS; hosted execution required |
| Docker/CI/CD packaging | Dockerfiles, Compose, Caddy and workflows retained | Static validation PASS; local Docker NOT RUN |

See `TEST_REPORT_1.5.2.md` and `test_evidence_1_5_2/` for actual evidence and limitations.
