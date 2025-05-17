"use client";

import { useEffect } from "react";
import i18next from "i18next";
import {
  initReactI18next,
  useTranslation as useTranslationOrg,
} from "react-i18next";
import resourcesToBackend from "i18next-resources-to-backend";
import LanguageDetector from "i18next-browser-languagedetector";

import { getCookie, setCookie } from "cookies-next";

import {
  cookieName,
  i18nOptions,
  Language,
  languages,
  Namespace,
} from "./conf";
import { Options } from ".";

const isServer = typeof window === "undefined";

i18next
  .use(initReactI18next)
  .use(LanguageDetector)
  .use(
    resourcesToBackend(
      (language: Language, namespace: Namespace) =>
        import(`./locales/${language}/${namespace}.yaml`)
    )
  )
  .init({
    ...i18nOptions,
    lng: undefined, // let detect the language on client side
    detection: {
      order: ["path", "htmlTag", "cookie", "navigator"],
    },
    preload: isServer ? languages : [],
  });

export function useTranslation(
  lang: Language,
  ns: Namespace,
  options: Options = {}
) {
  const ret = useTranslationOrg(ns, options);
  const { i18n } = ret;
  const i18nextCookie = getCookie(cookieName);

  // update i18n
  useEffect(() => {
    if (isServer) return;
    if (!lang || i18n.resolvedLanguage === lang) return;
    i18n.changeLanguage(lang);
  }, [lang, i18n]);

  // update cookie
  useEffect(() => {
    if (isServer) return;
    if (i18nextCookie === lang) return;
    setCookie(cookieName, lang, { path: "/" });
  }, [lang, i18nextCookie]);

  if (isServer && lang && i18n.resolvedLanguage !== lang) {
    i18n.changeLanguage(lang);
  }

  return ret;
}
