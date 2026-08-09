const LECTURE_TEMPLATES = [
  'Introduction & Foundational Concepts',
  'Core Operations & Basic Syntax',
  'Intermediate Problem Solving',
  'Practical Applications & Case Studies',
  'Advanced Techniques & Theory',
  'Optimization & Best Practices',
  'Team / Project Work',
  'Comprehensive Topic Review'
];

const GRADE_POINTS = {
  'A+': 4.00, 'A': 3.75, 'A-': 3.50,
  'B+': 3.25, 'B': 3.00, 'B-': 2.75,
  'C+': 2.50, 'C': 2.25, 'C-': 2.00,
  'D+': 1.75, 'D': 1.50, 'F': 0.00
};

const roundVal = (num) => {
  return Math.round(num * 100) / 100;
};

const min = (a, b) => {
  return a < b ? a : b;
};

const parseDate = (str) => {
  if (!str) return null;
  const d = new Date(str + 'T00:00:00');
  return isNaN(d.getTime()) ? null : d;
};

const weekIndexForDate = (startDate, date) => {
  const diffDays = Math.round((date - startDate) / (1000 * 60 * 60 * 24));
  return Math.floor(diffDays / 7) + 1;
};

const getGpaRating = (gpa) => {
  const val = parseFloat(gpa);
  if (isNaN(val) || val === 0.0) return 'Not Specified (غير محدد)';
  if (val < 2.0) return 'Under Probation (تحت الإنذار)';
  if (val >= 2.0 && val < 2.50) return 'Pass (مقبول)';
  if (val >= 2.50 && val < 3.00) return 'Good (جيد)';
  if (val >= 3.00 && val < 3.50) return 'Very Good (جيد جداً)';
  if (val >= 3.50 && val <= 4.00) return 'Excellent (ممتاز)';
  return 'Not Specified (غير محدد)';
};