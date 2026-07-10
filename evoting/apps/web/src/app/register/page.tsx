"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { CheckCircle2 } from "lucide-react";
import {
  geo,
  auth,
  type GeoState,
  type GeoDistrict,
  type GeoAssemblyBrief,
  type GeoAssemblyDetail,
  type Gender,
} from "@/lib/api";
import { errorMessage } from "@/lib/format";
import { Alert, Button, Card, Field, Input, Select } from "@/components/ui";

interface FormErrors {
  email?: string;
  password?: string;
  full_name?: string;
  dob?: string;
  aadhaar?: string;
  assembly?: string;
}

const AADHAAR_RE = /^\d{12}$/;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function RegisterPage() {
  // Account + identity
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [dob, setDob] = useState("");
  const [gender, setGender] = useState<Gender>("male");
  const [aadhaar, setAadhaar] = useState("");

  // Cascading geo selection
  const [states, setStates] = useState<GeoState[]>([]);
  const [districts, setDistricts] = useState<GeoDistrict[]>([]);
  const [assemblies, setAssemblies] = useState<GeoAssemblyBrief[]>([]);
  const [stateId, setStateId] = useState("");
  const [districtId, setDistrictId] = useState("");
  const [assemblyId, setAssemblyId] = useState("");
  const [assemblyDetail, setAssemblyDetail] = useState<GeoAssemblyDetail | null>(null);

  const [geoError, setGeoError] = useState<string | null>(null);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  // Load states once.
  useEffect(() => {
    geo
      .states()
      .then(setStates)
      .catch((err) => setGeoError(errorMessage(err)));
  }, []);

  // State -> districts
  useEffect(() => {
    setDistrictId("");
    setDistricts([]);
    setAssemblyId("");
    setAssemblies([]);
    setAssemblyDetail(null);
    if (!stateId) return;
    geo
      .districts(stateId)
      .then(setDistricts)
      .catch((err) => setGeoError(errorMessage(err)));
  }, [stateId]);

  // District -> assemblies
  useEffect(() => {
    setAssemblyId("");
    setAssemblies([]);
    setAssemblyDetail(null);
    if (!districtId) return;
    geo
      .assemblies(districtId)
      .then(setAssemblies)
      .catch((err) => setGeoError(errorMessage(err)));
  }, [districtId]);

  // Assembly -> detail (parliamentary constituency)
  useEffect(() => {
    setAssemblyDetail(null);
    if (!assemblyId) return;
    geo
      .assembly(assemblyId)
      .then(setAssemblyDetail)
      .catch((err) => setGeoError(errorMessage(err)));
  }, [assemblyId]);

  function validate(): boolean {
    const next: FormErrors = {};
    if (!EMAIL_RE.test(email)) next.email = "Enter a valid email address.";
    if (password.length < 8) next.password = "Password must be at least 8 characters.";
    if (fullName.trim().length < 2) next.full_name = "Enter your full name.";
    if (!dob) next.dob = "Enter your date of birth.";
    if (!AADHAAR_RE.test(aadhaar)) next.aadhaar = "Aadhaar must be exactly 12 digits.";
    if (!assemblyId) next.assembly = "Select your assembly constituency.";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitError(null);
    if (!validate()) return;
    setSubmitting(true);
    try {
      await auth.register({
        email,
        password,
        full_name: fullName,
        dob,
        gender,
        aadhaar,
        assembly_constituency_id: assemblyId,
      });
      setDone(true);
    } catch (err) {
      setSubmitError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  if (done) {
    return (
      <div className="mx-auto max-w-md px-4 py-16">
        <Card>
          <div className="flex flex-col items-center text-center">
            <CheckCircle2 className="h-12 w-12 text-emerald-500" aria-hidden />
            <h1 className="mt-4 text-2xl font-bold text-slate-900">Registration submitted</h1>
            <p className="mt-2 text-sm text-slate-600">
              Your account has been created and is <strong>pending approval</strong> by an
              election administrator. You can log in now to enroll your face while you wait.
            </p>
            <Link
              href="/login"
              className="mt-6 inline-flex w-full items-center justify-center rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500"
            >
              Continue to login
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-3xl font-bold text-slate-900">Register to vote</h1>
      <p className="mt-2 text-slate-600">
        Provide your identity details and choose your constituency. Fields marked with
        <span className="text-rose-600"> *</span> are required.
      </p>

      <Card className="mt-8">
        <form onSubmit={handleSubmit} className="space-y-6" noValidate>
          {submitError && <Alert tone="error">{submitError}</Alert>}

          {/* Account */}
          <fieldset className="space-y-4">
            <legend className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Account
            </legend>
            <Field label="Email *" htmlFor="email" error={errors.email}>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </Field>
            <Field
              label="Password *"
              htmlFor="password"
              hint="At least 8 characters."
              error={errors.password}
            >
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </Field>
          </fieldset>

          {/* Identity */}
          <fieldset className="space-y-4">
            <legend className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Identity
            </legend>
            <Field label="Full name *" htmlFor="full_name" error={errors.full_name}>
              <Input
                id="full_name"
                autoComplete="name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </Field>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Date of birth *" htmlFor="dob" error={errors.dob}>
                <Input
                  id="dob"
                  type="date"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                />
              </Field>
              <Field label="Gender *" htmlFor="gender">
                <Select
                  id="gender"
                  value={gender}
                  onChange={(e) => setGender(e.target.value as Gender)}
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </Select>
              </Field>
            </div>
            <Field
              label="Aadhaar number *"
              htmlFor="aadhaar"
              hint="12 digits, no spaces."
              error={errors.aadhaar}
            >
              <Input
                id="aadhaar"
                inputMode="numeric"
                maxLength={12}
                value={aadhaar}
                onChange={(e) => setAadhaar(e.target.value.replace(/\D/g, ""))}
              />
            </Field>
          </fieldset>

          {/* Constituency */}
          <fieldset className="space-y-4">
            <legend className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Constituency
            </legend>
            {geoError && <Alert tone="error">{geoError}</Alert>}
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="State *" htmlFor="state">
                <Select
                  id="state"
                  value={stateId}
                  onChange={(e) => setStateId(e.target.value)}
                >
                  <option value="">Select a state…</option>
                  {states.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="District *" htmlFor="district">
                <Select
                  id="district"
                  value={districtId}
                  disabled={!stateId || districts.length === 0}
                  onChange={(e) => setDistrictId(e.target.value)}
                >
                  <option value="">
                    {stateId ? "Select a district…" : "Select a state first"}
                  </option>
                  {districts.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
                </Select>
              </Field>
            </div>
            <Field
              label="Assembly constituency *"
              htmlFor="assembly"
              error={errors.assembly}
            >
              <Select
                id="assembly"
                value={assemblyId}
                disabled={!districtId || assemblies.length === 0}
                onChange={(e) => setAssemblyId(e.target.value)}
              >
                <option value="">
                  {districtId ? "Select an assembly…" : "Select a district first"}
                </option>
                {assemblies.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name} ({a.reservation})
                  </option>
                ))}
              </Select>
            </Field>

            {assemblyDetail && (
              <Alert tone="info">
                <p>
                  Parliamentary constituency:{" "}
                  <strong>{assemblyDetail.parliamentary_constituency_name}</strong>
                </p>
                <p className="mt-0.5 text-xs">
                  District: {assemblyDetail.district_name} · Reservation:{" "}
                  {assemblyDetail.reservation}
                </p>
              </Alert>
            )}
          </fieldset>

          <Button type="submit" className="w-full" loading={submitting}>
            Create account
          </Button>

          <p className="text-center text-sm text-slate-600">
            Already registered?{" "}
            <Link href="/login" className="font-medium text-indigo-600 hover:underline">
              Log in
            </Link>
          </p>
        </form>
      </Card>
    </div>
  );
}
