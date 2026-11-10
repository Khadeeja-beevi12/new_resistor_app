import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 100 },
    { duration: '1m', target: 500 },
    { duration: '1m', target: 1000 },
    { duration: '1m', target: 0 },
  ],
};

const BASE = 'http://127.0.0.1:8000';

const H = {
  headers: {
    'Content-Type': 'application/json',
  },
};

export default function () {

  // Get challenge
  const res = http.get(`${BASE}/api/challenge`);

  check(res, {
    'challenge status 200': (r) => r.status === 200,
  });

  const token = res.json('token');

  sleep(1);

  // Submit answer
  const chk = http.post(
    `${BASE}/api/check`,
    JSON.stringify({
      token: token,
      answer: '220',
    }),
    H
  );

  check(chk, {
    'check status 200': (r) => r.status === 200,
  });

  sleep(1);
}