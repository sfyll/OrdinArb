package main

import (
	"bufio"
	"bytes"
	"encoding/hex"
	"encoding/json"
	"log"
	"os"
	"strings"

	"github.com/balletcrypto/bitcoin-inscription-parser/parser"
	"github.com/btcsuite/btcd/wire"
)

const DUMP_FILE = "../dump/dump.txt"

type InscriptionType uint8

const (
    BRC20 InscriptionType = iota
    MRC721 
    Unknown
)

func loadRawTxs() []*wire.MsgTx {
	// open dump file
	file, err := os.Open(DUMP_FILE)
	if err != nil {
		log.Fatal(err)
	}

	// read dump file
	var msg_txs []*wire.MsgTx
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		new_line := scanner.Text()
		if "RawTransaction" == new_line[:14] {
			rhs := strings.Split(new_line, ",")[1]
			raw_tx := strings.Trim(strings.Split(rhs, "=")[1], " )")
            msg_tx, err := parseRawTxString(raw_tx)
            if err != nil {
                log.Fatal(err)
                continue
            }
			msg_txs = append(msg_txs, msg_tx)
		}
	}
	return msg_txs
}

func parseRawTxString(raw_tx string) (*wire.MsgTx, error) {
    raw_tx_bytes, err := hex.DecodeString(raw_tx)
    if err != nil {
        return nil, err
    }
    return parseRawTxBytes(raw_tx_bytes)
}

func parseRawTxBytes(raw_tx []byte) (*wire.MsgTx, error) {
    tx := wire.NewMsgTx(wire.TxVersion)
    return tx, tx.Deserialize(bytes.NewReader(raw_tx))
}

type Instruction struct {
    P string `json:"p"`
    Op string `json:"op"`
    Tick string `json:"tick,omitempty"`
    Amt string `json:"amt,omitempty"`
}

func parseInstruction(inscription *parser.TransactionInscription) *Instruction {
    contentType := string(inscription.Inscription.ContentType)
    if strings.ToLower(contentType) == "text/html;charset=utf-8" {
        return nil
    } else if strings.ToLower(contentType) == "text/plain;charset=utf-8" {
        contentBody := string(inscription.Inscription.ContentBody)
        content := new(Instruction)
        err := json.Unmarshal([]byte(contentBody), content)
        if err != nil {
            log.Printf("Error: %v", err)
            log.Printf("ContentBody: %s", contentBody)
            return nil
        }
        return content

    }
    return nil
}

func printInscription(inscription *parser.TransactionInscription) {
    log.Printf("TxInIndex: %d, TxInOffset: %d", inscription.TxInIndex, inscription.TxInOffset)
    log.Printf("ContentLength: %d", inscription.Inscription.ContentLength)
    log.Printf("ContentType: %s", hex.EncodeToString(inscription.Inscription.ContentType))
    log.Printf("ContentType as string: %s", string(inscription.Inscription.ContentType))
    log.Printf("ContentBody: %s", hex.EncodeToString(inscription.Inscription.ContentBody))
    log.Printf("ContentBody as string: %s", string(inscription.Inscription.ContentBody))
    log.Printf("IsUnrecognizedEvenField: %t", inscription.Inscription.IsUnrecognizedEvenField)
}

func main() {
	raw_txs := loadRawTxs()
    inscription_count := 0
    instruction_count := 0
    for _, raw_tx := range raw_txs {
        inscriptions := parser.ParseInscriptionsFromTransaction(raw_tx)
        if len(inscriptions) == 0 {
            continue
        }
        inscription_count += 1
        for _, inscription := range inscriptions {
            instruction := parseInstruction(inscription)
            if instruction == nil {
                continue
            }
            instruction_count += 1
            log.Printf("Instruction: %v", instruction)
        }
    }
    log.Printf("Total inscriptions: %d", inscription_count)
    log.Printf("Total instructions: %d", instruction_count)
}
