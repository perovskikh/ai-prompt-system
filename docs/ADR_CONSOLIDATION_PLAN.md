# ADR Consolidation & Verification Plan

**Date**: 2026-03-20
**Reference**: docs/BOTTLENECKS_ANALYSIS.md, promt-consolidation-simple.md
**Target**: Consolidate duplicate ADR-002 files and verify ADR integrity

---

## 📊 Current State Analysis

### Duplicate ADR Files Found

```
docs/explanation/adr/ADR-002-tiered-prompt-architecture-mpv-integration.md  (MAIN)
├── docs/explanation/adr/ADR-002-FINAL-REVIEW.md        (REVIEW - DUPLICATE)
├── docs/explanation/adr/ADR-002-REVIEW.md                (REVIEW - DUPLICATE)
└── (other potential duplicates...)
```

### Issue Analysis

**Problem**: ADR-002 appears in 3 separate files causing:
1. 📋 **Documentation confusion** - Which is the "real" ADR-002?
2. 🔢 **Topic slug conflict** - '002' appears in multiple files
3. ⚠️ **Pre-commit hook detection** - Fails on duplicate slugs
4. 📝 **Maintenance burden** - Need to update multiple files
5. 🎯 **Version control issues** - Hard to track changes

**Root Cause**: ADR-002 review process created separate review documents instead of using Git discussion features

**Impact**:
- ❌ Violates ADR-003 (Prompt Storage Strategy) - Single Source of Truth
- ❌ Confuses automated tools (pre-commit hooks, AI analysis)
- ❌ Reduces documentation quality (fragmented information)
- ❌ Creates merge conflicts

---

## 🎯 Consolidation Plan

### Phase 1: Analysis & Verification (Week 1)

#### 1.1 Content Analysis
**Task**: Analyze content of all ADR-002 variants

**Actions**:
```bash
# Compare content to determine what information is duplicated
python3 -c "
from pathlib import Path

main_adr = Path('docs/explanation/adr/ADR-002-tiered-prompt-architecture-mpv-integration.md')
review_files = [
    'docs/explanation/adr/ADR-002-FINAL-REVIEW.md',
    'docs/explanation/adr/ADR-002-REVIEW.md'
]

print('Main ADR size:', main_adr.stat().st_size)
for rf in review_files:
    if Path(rf).exists():
        print(f'Review: {rf} - {Path(rf).stat().st_size}')
"
```

**Success Criteria**:
- ✅ Identify unique content in each file
- ✅ Determine consolidation strategy
- ✅ Create verification checklist

**Estimated Time**: 2 hours

---

#### 1.2 Verification Plan
**Task**: Create verification checklist to ensure main ADR-002 contains all critical information

**Verification Checklist**:
```markdown
- [ ] Status is marked as "Implemented" (not "Accepted" or "Proposed")
- [ ] Decision section contains complete rationale
- [ ] Context section addresses the problem clearly
- [ ] Decision section states chosen approach with justification
- [ ] Consequences section lists pros/ cons
- [ ] All referenced files and links are correct
- [ ] Implementation notes are complete
- [ ] No contradictions between sections
- [ ] Format follows ADR template
- [ ] File is linked from ADR_INDEX.md
```

**Estimated Time**: 1 hour

---

### Phase 2: Content Consolidation (Week 2)

#### 2.1 Main ADR-002 Enhancement
**Task**: Enhance main ADR-002 to include review discussion summaries

**Actions**:
1. Add "Review History" section at the end of ADR-002
2. Summarize key points from FINAL-REVIEW
3. Summarize key points from REVIEW
4. Link to review discussion (even if files are removed)

**New Section to Add**:
```markdown
## Review History

### ADR-002-FINAL-REVIEW (2026-03-19)
**Status**: Final review completed
**Key Decisions**:
- Implementation approved with Phase 5 complete
- JWT, RBAC, HTTPS proxy confirmed
- Ready for production deployment

**Discussion Summary**:
- Implementation timeline: Phase 1-5 completed
- All blockers resolved
- Performance metrics meeting targets

### ADR-002-REVIEW (2026-03-XX)
**Status**: Interim review
**Key Points**: [extract from file]

---
*See also: Git commit history for detailed discussion*
```

**Estimated Time**: 2 hours

---

#### 2.2 Duplicate File Removal
**Task**: Move review files to separate directory to avoid confusion

**Actions**:
```bash
# Create reviews subdirectory
mkdir -p docs/explanation/adr/reviews/

# Move review files (with date prefixes)
mv docs/explanation/adr/ADR-002-FINAL-REVIEW.md docs/explanation/adr/reviews/
mv docs/explanation/adr/ADR-002-REVIEW.md docs/explanation/adr/reviews/

# Add README to reviews directory
cat > docs/explanation/adr/reviews/README.md << 'EOF'
# ADR Review Files

This directory contains historical ADR review documents.

## Purpose
- Archive review discussions separately from active ADRs
- Maintain ADR-002 main file as single source of truth
- Track review history for audit purposes

## Convention
- Review files are named: ADR-XXX-{TYPE}-{DATE}.md
- Types: FINAL-REVIEW, REVIEW, INTERIM-REVIEW
- Main ADR files remain in parent directory

## Access
- For current ADR status, see main ADR file in parent directory
- For historical review discussions, see files in this directory

---
*Last Updated: 2026-03-20*
EOF
```

**Estimated Time**: 30 minutes

---

#### 2.3 ADR Index Update
**Task**: Update ADR_INDEX.md to reflect consolidation

**Changes to ADR_INDEX.md**:
```markdown
| ADR # | Title | Status | Date | Focus |
|---------|--------|--------|--------|
| ADR-002 | [Tiered Prompt Architecture & MPV Integration](ADR-002-tiered-prompt-architecture-mpv-integration.md) | **Implemented** | 2026-03-19 | Tiered: 25 universal + 7 mpv + 4 pack |
```

**Estimated Time**: 15 minutes

---

### Phase 3: Verification & Testing (Week 3)

#### 3.1 Pre-commit Hook Validation
**Task**: Update pre-commit hook to properly handle review files

**Current Issue**: Pre-commit treats review files as duplicates

**Fix**: Add exclusion logic for reviews/ directory

```python
# Update .pre-commit-config.yaml or create proper .pre-commit-hooks/validate-adr.py
# Exclude docs/explanation/adr/reviews/ from duplicate detection
# Keep main ADR-002 in main directory
# Detect duplicates only within docs/explanation/adr/ (not subdirectories)
```

**Estimated Time**: 2 hours

---

#### 3.2 Automated Testing
**Task**: Test that pre-commit hook no longer fails on review files

**Test Cases**:
```bash
# Test 1: Create new ADR review file
touch docs/explanation/adr/reviews/TEST-REVIEW.md
python3 .pre-commit-config.yaml
# Expected: PASS (review files excluded)

# Test 2: Create duplicate in main directory
touch docs/explanation/adr/ADR-004-duplicate.md
python3 .pre-commit-config.yaml
# Expected: FAIL (duplicate detected)

# Test 3: Main ADR-002 still validates
python3 .pre-commit-config.yaml
# Expected: PASS (main ADR is valid)
```

**Estimated Time**: 1 hour

---

#### 3.3 AI Analysis Validation
**Task**: Verify AI bottleneck analysis handles consolidated ADRs correctly

**Test**:
```bash
# Run AI analysis on consolidated ADR
mcp__ai-prompt-system__ai_prompts request="проанализируй ADR-002 после консолидации" context='{
  "adr_file": "docs/explanation/adr/ADR-002-tiered-prompt-architecture-mpv-integration.md",
  "reference_doc": "docs/BOTTLENECKS_ANALYSIS.md"
}'
```

**Expected Result**: No duplicate ADR-002 errors detected

**Estimated Time**: 30 minutes

---

### Phase 4: Documentation & Deployment (Week 4)

#### 4.1 Update Documentation
**Task**: Update all related documentation to reflect consolidation

**Documents to Update**:
1. `docs/BOTTLENECKS_ANALYSIS.md` - Remove duplicate ADR-002 items
2. `docs/TECHNICAL_DEBT_TRACKER.md` - Update configuration debt status
3. `docs/AUTO_FIX_IMPLEMENTATION.md` - Update ADR handling
4. `docs/SYSTEM_TESTING_REPORT.md` - Add consolidation test results
5. `docs/explanation/adr/ADR_INDEX.md` - Already updated in Phase 2.3

**Estimated Time**: 3 hours

---

#### 4.2 Git Operations
**Task**: Commit consolidation changes with proper messages

**Commit Messages**:
```bash
# Commit 1: Main ADR-002 enhancement
git add docs/explanation/adr/ADR-002-tiered-prompt-architecture-mpv-integration.md
git commit -m "docs: enhance ADR-002 with review history

- Add Review History section
- Summarize FINAL-REVIEW and REVIEW discussions
- Maintain ADR-002 as single source of truth
- Refs: ADR-002 consolidation plan"

# Commit 2: Move review files
git add docs/explanation/adr/reviews/
git commit -m "docs: move ADR-002 review files to reviews/ subdirectory

- Archive historical ADR-002 reviews
- Create reviews/README.md
- Separate active ADRs from review discussions
- Fix pre-commit hook duplicate detection
- Refs: ADR-002 consolidation plan"

# Commit 3: Update ADR_INDEX.md
git add docs/explanation/adr/ADR_INDEX.md
git commit -m "docs: update ADR_INDEX.md with consolidated ADR-002 status

- ADR-002 marked as Implemented
- Review files moved to reviews/ subdirectory
- Updated focus description
- Refs: ADR-002 consolidation plan"

# Commit 4: Update documentation
git add docs/
git commit -m "docs: update all documentation for ADR-002 consolidation

- Update BOTTLENECKS_ANALYSIS.md
- Update TECHNICAL_DEBT_TRACKER.md
- Update AUTO_FIX_IMPLEMENTATION.md
- Update SYSTEM_TESTING_REPORT.md
- Refs: ADR-002 consolidation plan"

# Create tag for tracking
git tag -a adr-002-consolidated -m "ADR-002 consolidated: review files moved, main ADR enhanced"
```

**Estimated Time**: 1 hour

---

## 📅 Timeline Summary

| Phase | Tasks | Duration | Start Date | End Date |
|--------|--------|------------|-----------|
| **Phase 1: Analysis** | 1.1, 1.2 | 3 hours | Week 1 | 2026-03-20 | 2026-03-22 |
| **Phase 2: Consolidation** | 2.1, 2.2, 2.3 | 3.5 hours | Week 2 | 2026-03-23 | 2026-03-25 |
| **Phase 3: Verification** | 3.1, 3.2, 3.3 | 3.5 hours | Week 3 | 2026-03-26 | 2026-03-28 |
| **Phase 4: Documentation** | 4.1, 4.2 | 4 hours | Week 4 | 2026-03-29 | 2026-04-02 |

**Total Duration**: **14 hours** (~2 days)
**Target Completion**: 2026-04-02

---

## ✅ Success Criteria

### Completion Checklist

#### Documentation
- [x] ADR Consolidation Plan created
- [ ] ADR-002 enhanced with review history
- [ ] Review files moved to reviews/ subdirectory
- [ ] ADR_INDEX.md updated
- [ ] All documentation updated

#### Verification
- [ ] Pre-commit hook updated to exclude reviews/
- [ ] No duplicate ADR-002 errors in pre-commit
- [ ] AI analysis validates consolidated ADR correctly
- [ ] All test cases pass

#### Git Operations
- [ ] Consolidation changes committed
- [ ] Proper commit messages used
- [ ] Tag created: adr-002-consolidated
- [ ] Pushed to repository

#### Integration
- [ ] CI/CD pipeline validates new structure
- [ ] No errors in GitHub Actions
- [ ] Documentation builds successfully
- [ ] Links are correct

---

## 🎯 Expected Outcomes

### After Consolidation

**Documentation Structure**:
```
docs/explanation/adr/
├── ADR-001-system-genesis.md
├── ADR-002-tiered-prompt-architecture-mpv-integration.md  (ENHANCED)
├── ADR-003-prompt-storage-strategy.md
├── ADR_INDEX.md
└── reviews/                                     (NEW DIRECTORY)
    ├── README.md
    ├── ADR-002-FINAL-REVIEW.md
    ├── ADR-002-REVIEW.md
    └── [future review files]
```

**Benefits**:
- ✅ Single Source of Truth for ADR-002
- ✅ Clear separation of active ADRs and review history
- ✅ No more duplicate topic slug '002' errors
- ✅ Pre-commit hook works correctly
- ✅ Better maintainability
- ✅ Complies with ADR-003 (Prompt Storage Strategy)

### Metrics

| Metric | Before | After | Improvement |
|---------|---------|--------|-------------|
| ADR-002 duplicates | 3 files | 0 files | -100% |
| Pre-commit errors | Duplicate slug errors | None | ✅ |
| Documentation clarity | Confusing | Clear | ✅ |
| Maintenance burden | High | Low | ✅ |

---

## 🔄 Rollback Plan

**If consolidation causes issues**:

1. **Immediate**: Create rollback branch
   ```bash
   git checkout -b rollback-adr-002-consolidation
   ```

2. **Restore**: Restore original structure
   ```bash
   git revert --main HEAD~4  # Revert all 4 commits
   ```

3. **Verify**: Test that original structure works
   ```bash
   python3 .pre-commit-config.yaml  # Should pass
   ```

4. **Report**: Document rollback reason and alternative approach

---

## 📚 References

- **[Bottleneck Analysis](BOTTLENECKS_ANALYSIS.md)** - Configuration debt items 10-11
- **[ADR-002](docs/explanation/adr/ADR-002-tiered-prompt-architecture-mpv-integration.md)** - Main ADR file
- **[ADR-003](docs/explanation/adr/ADR-003-prompt-storage-strategy.md)** - Storage strategy requirements
- **[Promt Consolidation Simple](prompts/universal/ai_agent_prompts/promt-consolidation-simple.md)** - Consolidation prompt (not working via run_prompt)

---

**Status**: 📋 **READY FOR IMPLEMENTATION**
**Priority**: 🟢 **MEDIUM**
**Estimated Time**: 14 hours (~2 days)
**Owner**: Development Team
**Next Review**: 2026-04-02