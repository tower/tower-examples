# Hello World

A minimal Tower app that prints a greeting message. This is the simplest example to get started with Tower.

## What It Does

The app prints a greeting 5 times, saying hello to a friend and boo to a foe. It demonstrates how to use Tower app parameters.

## App Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `friend` | Someone that is close to you | `Steve` |
| `foe` | Something that you'd prefer to avoid | `Carl` |

## Running Locally

Run with Tower local mode:

```bash
tower run --local
```

Run with custom parameters:

```bash
tower run --local --parameter=friend="Alice" --parameter=foe="Bob"
```

## Deploying to Tower

### Deploy the App

```bash
tower deploy
```

If the app doesn't exist, Tower will prompt you to create it.

### Run on Tower Cloud

```bash
tower run
```

Run with custom parameters:

```bash
tower run --parameter=friend="Alice" --parameter=foe="Bob"
```

## Monitoring

Check run status:

```bash
tower apps show
```

View logs:

```bash
tower apps logs hello-world#1
```
