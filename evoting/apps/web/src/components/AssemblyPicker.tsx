"use client";

import { useEffect, useState } from "react";
import {
  geo,
  type GeoState,
  type GeoDistrict,
  type GeoAssemblyBrief,
} from "@/lib/api";
import { errorMessage } from "@/lib/format";
import { Alert, Field, Select } from "./ui";

interface AssemblyPickerProps {
  value: string;
  onChange: (assemblyId: string) => void;
  idPrefix?: string;
}

/** Cascading State → District → Assembly selector. Emits the assembly id. */
export function AssemblyPicker({ value, onChange, idPrefix = "ap" }: AssemblyPickerProps) {
  const [states, setStates] = useState<GeoState[]>([]);
  const [districts, setDistricts] = useState<GeoDistrict[]>([]);
  const [assemblies, setAssemblies] = useState<GeoAssemblyBrief[]>([]);
  const [stateId, setStateId] = useState("");
  const [districtId, setDistrictId] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    geo.states().then(setStates).catch((err) => setError(errorMessage(err)));
  }, []);

  useEffect(() => {
    setDistrictId("");
    setDistricts([]);
    setAssemblies([]);
    onChange("");
    if (!stateId) return;
    geo.districts(stateId).then(setDistricts).catch((err) => setError(errorMessage(err)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stateId]);

  useEffect(() => {
    setAssemblies([]);
    onChange("");
    if (!districtId) return;
    geo
      .assemblies(districtId)
      .then(setAssemblies)
      .catch((err) => setError(errorMessage(err)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [districtId]);

  return (
    <div className="space-y-4">
      {error && <Alert tone="error">{error}</Alert>}
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="State" htmlFor={`${idPrefix}-state`}>
          <Select
            id={`${idPrefix}-state`}
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
        <Field label="District" htmlFor={`${idPrefix}-district`}>
          <Select
            id={`${idPrefix}-district`}
            value={districtId}
            disabled={!stateId}
            onChange={(e) => setDistrictId(e.target.value)}
          >
            <option value="">{stateId ? "Select a district…" : "Select a state first"}</option>
            {districts.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </Select>
        </Field>
      </div>
      <Field label="Assembly constituency" htmlFor={`${idPrefix}-assembly`}>
        <Select
          id={`${idPrefix}-assembly`}
          value={value}
          disabled={!districtId}
          onChange={(e) => onChange(e.target.value)}
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
    </div>
  );
}
